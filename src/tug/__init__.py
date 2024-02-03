from loguru import logger
import os
import sys
from pathlib import Path
from collections import defaultdict
import tomllib
from typing import Any, Optional
from importlib import resources

from PyQt6.QtCore import QSettings, QVariant, QFile, QTextStream
from PyQt6.QtGui import QIcon, QPixmap

from src import qss

config = {}
open_db = None

APP_NAME = "fileo"
MAKER = 'miha'

settings = None
qss_params = {}
dyn_qss = defaultdict(list)
m_icons = defaultdict(list)

def create_dir(dir: Path):
    dir.mkdir(parents=True, exist_ok=True)

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

def save_to_file(filename: str, msg: str):
    """ save translated qss """
    pp = Path('~/fileo/report').expanduser()
    path = get_app_setting(
        'DEFAULT_REPORT_PATH', pp.as_posix()
    )
    path = Path(path) / filename

    flqss = QFile(path.as_posix())
    flqss.open(QFile.OpenModeFlag.WriteOnly)
    stream = QTextStream(flqss)
    stream << msg
    stream.flush()
    flqss.close()

def get_log_path() -> str:
    log_path = get_app_setting("DEFAULT_LOG_PATH", "")
    r_path = Path(log_path) if log_path else Path().resolve()
    return r_path

def set_logger():
    logger.remove()
    use_logging = int(get_app_setting("SWITCH_ON_LOGGING", 0))
    if not use_logging:
        return

    fmt = "{time:%y-%b-%d %H:%M:%S} | {level} | {module}.{function}({line}): {message}"

    log_path = (get_log_path() / 'fileo.log').as_posix()
    logger.add(log_path, format=fmt, rotation="1 days", retention=3)
    # logger.add(sys.stderr,  format='"{file.path}", line {line}, {function} - {message}')
    logger.info(f"START =================> {log_path}")

set_logger()

if sys.platform.startswith("win"):
    cfg_path = Path(os.getenv('LOCALAPPDATA')) / 'fileo/config.toml'
elif sys.platform.startswith("linux"):
    cfg_path = Path(os.getenv('HOME')) / '.local/share/fileo/config.toml'
logger.info(f'{cfg_path=}')

if cfg_path.exists():
    with open(cfg_path, "r") as ft:
        fileo_toml = ft.read()
else:
    fileo_toml = resources.read_text(qss, "fileo.toml")
    create_dir(cfg_path.parent)
    save_to_file(cfg_path, fileo_toml)
config = tomllib.loads(fileo_toml)

def translate_qss(styles: str) -> str:
    for key, val in qss_params.items():
        styles = styles.replace(key, val)
    return styles

def prepare_styles(theme: str, to_save: bool = False) -> str:
    global icons_res

    def parse_params(params):
        global qss_params
        params = [it.split('~') for it in params.split('\n') if it.startswith("$") and ('~' in it)]
        params.sort(key=lambda x: x[0], reverse=True)
        qss_params = {key.strip():value.strip() for key,value in params}
        param_substitution()

    def param_substitution():
        for key, val in qss_params.items():
            if key.startswith("$ico_"):
                qss_params[key] = '/'.join((res_path, val))
            elif key.startswith("$"):
                qss_params[key] = val

    def extract_dyn_qss() -> int:
        it = tr_styles.find("/* END")
        aa: str = tr_styles
        it2 = aa.find('##', it)
        lines = tr_styles[it2:].split("\n")
        dyn_qss_add_lines(lines)
        return it

    def dyn_qss_add_lines(lines: list[str]):
        global dyn_qss
        for line in lines:
            if line.startswith('##'):
                key, val = line.split('~')
                dyn_qss[key[2:]].append(val)

    with resources.path(qss, "default.qss") as pic_path:
        res_path = pic_path.parent.as_posix()

    styles = resources.read_text(qss, '.'.join((theme, "qss")))
    params = resources.read_text(qss, '.'.join((theme, "param")))

    parse_params(params)
    tr_styles = translate_qss(styles)
    start_dyn = extract_dyn_qss()

    icons_txt = resources.read_text(qss, "icons.toml")
    tr_icons = translate_qss(icons_txt)
    icons_res = tomllib.loads(tr_icons)

    if to_save:
        save_to_file('QSS.log', tr_styles)
        save_to_file('icons.toml.log', tr_icons)

    collect_all_icons()

    return tr_styles[:start_dyn]

def collect_all_icons():
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
        'busy': ('busy_on', 'busy_off',),
        'show_hide': ('show_hide_off', 'show_hide_on'),
        'btnFilterSetup': ('filter_setup', 'filter_setup_active'),
        'btnDir': ('folders', 'folders_active'),
        'btnSetup': ('menu', ),
        'btnFilter': ('filter', 'filter_active'),
        'btnToggleBar': ('angle_left', 'angle_right'),
        'more': ('more',),
        'refresh': ('refresh',),
        'collapse_all': ('collapse_all',),
        'plus': ('plus',),
        'cancel2': ('cancel2',),
        'up': ('angle_up',),
        'down': ('angle_down',),
        'right': ('angle_right_2',),
        'toEdit': ('pencil',),
        'folder_open': ('folder_open',),
        'minimize': ('minimize',),
        'maximize': ('maximize', 'restore'),
        'close': ('close', 'close_active'),
    }
    set_icons(keys)

def get_icon(key: str, index: int = 0) -> QIcon:
    return m_icons[key][index]

def set_icons(keys: dict):
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

    def get_pixmaps(svg_key: str) -> list|None:
        def get_svg() -> str:
            ico_subst = ico_svg.get('ico_subst', '')
            if ico_subst:
                ico_svg2 = icons_res[ico_subst]
                return ico_svg2.get('ico', ''), ico_svg.get('colors', '')
            return ico_svg.get('ico', ''), ico_svg.get('colors', '')

        def create_pixs():
            def set_color() -> str:
                tmp = clr.split('|')
                if len(tmp) == 1:
                    tmp.insert(0, 'normal')
                return tmp[0], tmp[1].join(svg.split('|'))

            pix = []
            for clr in colors:
                mm, svg_ico = set_color()
                px = QPixmap()
                px.loadFromData(bytearray(svg_ico, 'utf-8'),)
                pix.append((mm, px))

            return pix

        def create_pix():
            px = QPixmap()
            px.loadFromData(bytearray(svg, 'utf-8'),)
            return [('normal', px)]

        ico_svg: dict = icons_res.get(svg_key, "")
        if not ico_svg:
            return []

        svg, colors = get_svg()
        return create_pixs() if colors else create_pix()

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
