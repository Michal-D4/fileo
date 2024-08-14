from loguru import logger
import os
import sys
import subprocess
from pathlib import Path
from collections import defaultdict
import tempfile
import tomllib
from typing import Any, Optional
from importlib import resources

from PyQt6.QtCore import QSettings, QVariant
from PyQt6.QtGui import QIcon, QPixmap

from .. import qss

if sys.platform.startswith("win"):
    def reveal_file(path: str):
        pp = Path(path)
        subprocess.run(['explorer.exe', '/select,', str(pp)])

elif sys.platform.startswith("linux"):
    def reveal_file(path: str):
        cmd = [
            'dbus-send', '--session', '--dest=org.freedesktop.FileManager1',
            '--type=method_call', '/org/freedesktop/FileManager1',
            'org.freedesktop.FileManager1.ShowItems',
            f'array:string:file:////{path}', 'string:',
        ]
        subprocess.run(cmd)
else:
    def reveal_file(path: str):
        raise NotImplemented(f"doesn't support {sys.platform} system")


APP_NAME = "fileo"
MAKER = 'miha'

open_db = None  # keep OpenDB instance, need !!!
config = {}
settings = None
qss_params = {}
dyn_qss = defaultdict(list)
m_icons = defaultdict(list)
themes = {}

#region  function_used_in___init___py
def get_app_setting(key: str, default: Optional[Any]=None) -> QVariant:
    """
    used to restore settings on application level
    """
    global settings
    if not settings:
        settings = QSettings(MAKER, APP_NAME)
    try:
        to_set = settings.value(key, default)
    except (TypeError, SystemError) as e:
        to_set = default
    return to_set

def get_log_path() -> str:
    report_path = get_app_setting("DEFAULT_REPORT_PATH", "")
    parent = Path(report_path).parent if report_path else Path()
    return config.get('log_path', parent / 'log')

def set_logger():
    logger.remove()
    use_logging = config.get('logging', False)
    if not use_logging:
        return

    fmt = "{time:%y-%b-%d %H:%M:%S} | {level} | {module}.{function}({line}): {message}"

    log_path = get_log_path() / 'fileo.log'
    logger.add(str(log_path), format=fmt, rotation="1 days", retention=3)
    # logger.add(sys.stderr,  format='"{file.path}", line {line}, {function} - {message}')
    logger.info(f"START =================> {log_path.as_posix()}")
    logger.info(f'cfg_path={cfg_path.as_posix()}')
#endregion

if sys.platform.startswith("win"):
    cfg_path = Path(os.getenv('LOCALAPPDATA')) / 'fileo/config.toml'
elif sys.platform.startswith("linux"):
    cfg_path = Path(os.getenv('HOME')) / '.local/share/fileo/config.toml'

if cfg_path.exists():
    with open(cfg_path, "r") as ft:
        fileo_toml = ft.read()
    cfg_path: Path = cfg_path.parent
else:
    fileo_toml = resources.read_text(qss, "fileo.toml")
    cfg_path: Path = Path(qss.__path__)

config = tomllib.loads(fileo_toml)

set_logger()

theme_toml_file = cfg_path / "themes.toml"
if theme_toml_file.exists():
    with open(theme_toml_file, "rb") as f:
        themes = tomllib.load(f)

temp_dir = tempfile.TemporaryDirectory()

def create_dir(dir: Path):
    dir.mkdir(parents=True, exist_ok=True)

def save_to_file(filename: str, msg: str):
    """ save translated qss """
    pp = Path('~/fileo/report').expanduser()
    path = get_app_setting('DEFAULT_REPORT_PATH', str(pp))
    path = Path(path) / filename
    path.write_text(msg)

def save_app_setting(**kwargs):
    """
    used to save settings on application level
    """
    if not kwargs:
        return
    global settings
    if not settings:
        settings = QSettings(MAKER, APP_NAME)

    for key, value in kwargs.items():
        settings.setValue(key, QVariant(value))

def translate_qss(styles: str) -> str:
    for key, val in qss_params.items():
        styles = styles.replace(key, val)
    return styles

def prepare_styles(theme_key: str, to_save: bool = False) -> str:
    global qss_params
    icons_txt = styles = params = ''
    dyn_qss.clear()

    def default_theme():
        nonlocal icons_txt, styles, params
        styles = resources.read_text(qss, "default.qss")
        params = resources.read_text(qss, "default.param")
        icons_txt = resources.read_text(qss, "icons.toml")

    def read_theme():
        def read_params():
            nonlocal params
            _param = theme.get('param', '') or "default.param"
            par_file = cfg_path / _param
            if par_file.exists():
                with open(par_file, "r") as ft:
                    params = ft.read()
            else:
                params = resources.read_text(qss, _param)

        def read_qss():
            nonlocal styles
            _qss = theme.get('qss', '')
            if not _qss:
                styles = resources.read_text(qss, "default.qss")
            else:
                qss_file = cfg_path / _qss
                if qss_file.exists():
                    with open(cfg_path / _qss, "r") as ft:
                        styles = ft.read()
                else:
                    styles = resources.read_text(qss, _qss)

        def read_ico():
            nonlocal icons_txt
            _ico = theme.get('ico', '')
            if not _ico:
                icons_txt = resources.read_text(qss, "icons.toml")
            else:
                ico_file = cfg_path / _ico
                if ico_file.exists():
                    with open(ico_file, "r") as ft:
                        icons_txt = ft.read()
                else:
                    icons_txt = resources.read_text(qss, _ico)

        nonlocal icons_txt, styles, params
        logger.info(f'{theme_key=}')
        if theme_key == "Default_Theme":
            default_theme()
            return

        theme = themes.get(theme_key, {})

        read_qss()
        read_params()
        read_ico()

    def parse_params(params):
        global qss_params
        params = [it.split('~') for it in params.splitlines() if it.startswith("$") and ('~' in it)]
        check_for_double_key(params)
        params.sort(key=lambda x: x[0], reverse=True)
        qss_params = {key.strip():value.strip() for key,value in params}
        param_substitution()

    def check_for_double_key(params: list):
        seen = set()
        for name, _ in params:
            if name in seen:
                raise Exception(f'Duplicate key "{name}" in qss parameters')
            seen.add(name)

    def param_substitution():
        global qss_params
        def val_subst(val: str) -> str:
            nonlocal loop_check
            if val.startswith("$"):
                if val in loop_check:
                    raise Exception(f'Loop in parameter {val} substitution')
                loop_check.add(val)
                return val_subst(qss_params[val])
            return val

        with resources.path(qss, qss_params['$ico_app']) as _path:
            qss_params['$ico_app'] = str(_path)
        for key, val in qss_params.items():
            loop_check = set(key)
            qss_params[key] = val_subst(val)

    def extract_dyn_qss() -> int:
        it = tr_styles.find("/* END")
        aa: str = tr_styles
        it2 = aa.find('##', it)
        lines = tr_styles[it2:].splitlines()
        dyn_qss_add_lines(lines)
        return it

    def dyn_qss_add_lines(lines: list[str]):
        for line in lines:
            if line.startswith('##'):
                key, val = line.split('~')
                dyn_qss[key[2:]].append(val)

    read_theme()

    parse_params(params)

    tr_icons = translate_qss(icons_txt)
    icons_res = tomllib.loads(tr_icons)

    svgs = collect_all_icons(icons_res)

    params = [(key, val) for key, val in qss_params.items()]
    params.sort(key=lambda x: x[0], reverse=True)
    qss_params = {key:value for key,value in params}

    tr_icons = translate_qss(icons_txt)
    icons_res = tomllib.loads(tr_icons)


    tr_styles = translate_qss(styles)
    start_dyn = extract_dyn_qss()

    if to_save:
        save_to_file(f'{theme_key}_QSS.log', tr_styles)
        save_to_file(f'{theme_key}_qss-params.log',
            '\n'.join([f'{key}: {val}' for key, val in qss_params.items()])
        )
        save_to_file(f'{theme_key}_icons.toml.log', tr_icons)
        svgs_str = '\n'.join([f'{key}:{val}' for key, val in svgs.items()])
        save_to_file(f'{theme_key}_svgs.log', svgs_str)

    return tr_styles[:start_dyn]

def get_dyn_qss(key: str, idx: int=0) -> str|list:
    qss = dyn_qss[key]
    if not qss:
        raise Exception(f'Not defined "{key}" qss')
    return dyn_qss[key][idx] if idx >= 0 else dyn_qss[key]

def collect_all_icons(icons_res: dict) -> dict:
    m_icons.clear()
    keys = {
        'folder': ('alphaF',),
        'hidden': ('alphaH',),
        'link': ('alphaL',),
        'prev_folder': ('arrow_back',),
        'next_folder': ('arrow_forward',),
        'history': ('history',),
        'search': ('search',),
        'match_case': ('match_case',),
        'match_word': ('match_word',),
        'ok': ('ok',),
        'busy': ('busy_off', 'busy_on',),
        'show_hide': ('show_hide_off', 'show_hide_on',),
        'btnFilterSetup': ('filter_setup', 'filter_setup_active',),
        'btnDir': ('folders', 'folders_active',),
        'btnSetup': ('menu', ),
        'btnFilter': ('filter', 'filter_active',),
        'btnToggleBar': ('angle_left', 'angle_right',),
        'more': ('more',),
        'refresh': ('refresh',),
        'collapse_all': ('collapse_all',),
        'collapse_notes': ('collapse_notes',),
        'plus': ('plus',),
        'cancel2': ('cancel2',),
        'up': ('angle_up',),
        'down': ('angle_down',),
        'right': ('angle_right_2',),
        'down3': ('angle_down_3',),
        'right3': ('angle_right_3',),
        'toEdit': ('pencil',),
        'folder_open': ('folder_open',),
        'minimize': ('minimize',),
        'maximize': ('maximize', 'restore',),
        'close': ('close',),
        'ico_app': ('app_ico',),
        'svg_files': (
            'check_box_off', 'check_box_on',
            'radio_btn',
            'vline3', 'angle_down3', 'angle_right3',
            'angle_down2',
        ),
    }
    return set_icons(keys, icons_res)

def get_icon(key: str, index: int = 0) -> QIcon:
    return m_icons[key][index]

def set_icons(keys: dict, icons_res: dict) -> dict:
    """
    add items into dict m_icons:
    keys - dict of list of svgs
    created item contains list of icons
    """
    mode = {
        'normal':  QIcon.Mode.Normal,
        'disabled':  QIcon.Mode.Disabled,
        'active':  QIcon.Mode.Active,
        'selected':  QIcon.Mode.Selected,
    }
    svgs = {}

    def get_pixmaps(svg_key: str) -> list|None:
        def get_svg() -> str:
            ico_subst = svg_stamp.get('ico_subst', '')
            if ico_subst:
                svg_root = icons_res[ico_subst]
                return svg_root.get('ico', ''), svg_stamp.get('colors', '')
            return svg_stamp.get('ico', ''), svg_stamp.get('colors', '')

        def get_colors():
            def get_color() -> tuple:
                """
                returns (mode, color)
                default mode is normal
                """
                tmp = clr.split('|')
                return tmp if len(tmp) == 2 else ('normal', tmp[0])

            colors = defaultdict(list)

            for clr in color_set:
                mm, color = get_color()
                colors[mm].append(
                    color if color else
                    colors['normal'][len(colors[mm])]
                )
            return colors

        def create_pixs():
            nonlocal svg
            colors = get_colors()
            pics = []
            if not colors:
                pic = QPixmap()
                pic.loadFromData(bytearray(svg, 'utf-8'),)
                pics.append(('normal', pic))
                return pics

            for mode_, color in colors.items():
                tmp = svg
                for i in range(svg.count('|')):
                    j = i % len(color)
                    tmp = tmp.replace('|', color[j], 1)
                svgs[f'{svg_key}_{mode_}'] = tmp

                if file_name:
                    create_image_file(mode_, tmp)
                    continue
                pic = QPixmap()
                pic.loadFromData(bytearray(tmp, 'utf-8'),)
                pics.append((mode_, pic))

            return pics

        def create_image_file(icon_mode: str, svg: str):
            # logger.info(f'{file_name=}, {icon_mode=}')
            if icon_mode == 'normal':
                file_ = Path(temp_dir.name) / f'{file_name}.svg'
            else:
                file_ = Path(temp_dir.name) / f'{file_name}_{icon_mode}.svg'
            qss_params[f'${file_.stem}'] = file_.as_posix()
            # logger.info(f'{file_.stem=}: {file_.as_posix()}')

            file_.write_text(svg)

        svg_stamp: dict = icons_res.get(svg_key, "")
        if not svg_stamp:
            return []

        svg, color_set = get_svg()
        file_name = svg_stamp.get('save_in_file', '')
        return create_pixs()

    def create_icon():
        pixs = get_pixmaps(svg_key)

        ico = QIcon()
        for mm, px in pixs:
            # logger.info(f'{key=}, {mm=}')
            ico.addPixmap(px, mode=mode[mm])

        # logger.info(f'{key=}, {[p[0] for p in pixs]}')
        m_icons[key].append(ico)

    for key, svg_keys in keys.items():
        # logger.info(f'{key=}, {svg_keys=}')
        for svg_key in svg_keys:
            create_icon()

    return svgs
