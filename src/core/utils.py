import sys
from loguru import logger

from pathlib import Path

from PyQt6.QtWidgets import QMessageBox

from . import app_globals as ag
from src import tug


def show_message_box(
        title: str, msg: str,
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
    else:
        dlg.setStandardButtons(btn)
        dlg.setIcon(icon)

    return dlg.exec()

def get_log_path() -> str:
    log_path = tug.get_app_setting("DEFAULT_LOG_PATH", "")
    r_path = Path(log_path) if log_path else Path().resolve()
    return r_path

def set_logger():
    logger.remove()
    use_logging = int(tug.get_app_setting("SWITCH_ON_LOGGING", 0))
    if not use_logging:
        return

    fmt = "{time:%y-%b-%d %H:%M:%S} | {level} | {module}.{function}({line}): {message}"

    log_path = (get_log_path() / 'fileo.log').as_posix()
    logger.add(log_path, format=fmt, rotation="1 days", retention=3)
    # logger.add(sys.stderr,  format='"{file.path}", line {line}, {function} - {message}')
    logger.info(f"START =================> {log_path}")
    logger.info(f'{ag.app_name()=}, {ag.app_version()=}')
