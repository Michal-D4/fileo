import sys
from loguru import logger

from pathlib import Path
from typing import Any, Optional
from importlib import resources

from PyQt6.QtCore import QSettings, QVariant, QFile, QTextStream
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QApplication, QMessageBox

from . import icons, app_globals as ag
from .. import qss as style_sheets

APP_NAME = "fileo"
MAKER = 'miha'

settings = None


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
    flqss.open(QFile.WriteOnly)
    stream = QTextStream(flqss)
    stream << msg
    stream.flush()
    flqss.close()

def apply_style(app: QApplication, theme: str, to_save: bool = False):
    params = None
    qss = None

    with resources.path(style_sheets, "search.svg") as pic_path:
        res_path = pic_path.parent.as_posix()

    def get_qss_theme():
        nonlocal params
        nonlocal qss
        qss = resources.read_text(style_sheets, '.'.join((theme, "qss")))
        params = resources.read_text(style_sheets, '.'.join((theme, "param")))

    def param_substitution():
        for key, val in ag.qss_params.items():
            if key.startswith("$ico_"):
                ag.qss_params[key] = '/'.join((res_path, val))
            elif key.startswith("$"):
                ag.qss_params[key] = val

    def parse_params():
        nonlocal params
        params = [it.split('~') for it in params.split('\n') if it.startswith("$") and ('~' in it)]
        params.sort(key=lambda x: x[0], reverse=True)
        ag.qss_params = {key.strip():value.strip() for key,value in params}
        param_substitution()

    def translate_qss():
        nonlocal params
        nonlocal qss
        parse_params()
        for key, val in ag.qss_params.items():
            qss = qss.replace(key, val)

    def dyn_qss_add_lines(lines: list[str]):
        for line in lines:
            if line.startswith('##'):
                key, val = line.split('~')
                ag.dyn_qss[key[2:]].append(val)

    def extract_dyn_qss() -> int:
        nonlocal qss
        it = qss.find("/* END")
        aa: str = qss
        it2 = aa.find('##', it)
        lines = qss[it2:].split("\n")
        dyn_qss_add_lines(lines)
        return it

    get_qss_theme()
    translate_qss()
    start_dyn = extract_dyn_qss()
    app.setStyleSheet(qss[:start_dyn])

    if to_save:
        save_to_file('QSS.log', qss)

    icons.collect_all_icons()

    icons.add_other_icon(
        'search', QPixmap(ag.qss_params['$ico_search'])
    )
    icons.add_other_icon(
        'match_case', QPixmap(ag.qss_params['$ico_match_case'])
    )
    icons.add_other_icon(
        'match_word', QPixmap(ag.qss_params['$ico_match_word'])
    )
    icons.add_other_icon(
        'app', QPixmap(ag.qss_params['$ico_app'])
    )

    try:
        from ctypes import windll  # to show icon on the taskbar - Windows only
        myappid = '.'.join((MAKER, APP_NAME))
        windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except ImportError:
        pass

    app.setWindowIcon(icons.get_other_icon("app"))

def show_message_box(title: str, msg: str,
                     custom_btns=None,
                     btn: QMessageBox.StandardButton = QMessageBox.StandardButton.Close,
                     icon: QMessageBox.Icon = QMessageBox.Icon.Information,
                     details: str = '') -> int:
    dlg = QMessageBox(ag.app)
    dlg.setWindowTitle(title)
    dlg.setText(msg)
    dlg.setDetailedText(details)
    if custom_btns:
        btns = []
        for btn in custom_btns:
            btns.append(dlg.addButton(*btn))
        dlg.setIcon(icon)
        dlg.exec()
        clicked = dlg.clickedButton()
        return btns.index(clicked) if clicked else -1
    else:
        dlg.setStandardButtons(btn)
        dlg.setIcon(icon)
        return dlg.exec()

def get_log_file_name() -> str:
    from datetime import datetime as dt
    log_path = get_app_setting("DEFAULT_LOG_PATH", "")
    r_path = Path(log_path) if log_path else Path().resolve()
    file_name = f"{dt.now():%b %d %H.%M.%S}.log"
    file = r_path / file_name
    return file.as_posix()

def set_logger():
    logger.remove()
    use_logging = int(get_app_setting("SWITCH_ON_LOGGING", 0))
    if not use_logging:
        return

    fmt = "{time:%y-%b-%d %H:%M:%S} | {level} | {module}.{function}({line}): {message}"

    LOG_FILE = get_log_file_name()
    logger.add(LOG_FILE, format=fmt, enqueue=True)
    logger.info(f'{ag.PID=}, {ag.app_name()=}, {ag.app_version()=}')
    logger.info(f"START =================> {LOG_FILE}")
