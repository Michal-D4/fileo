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

def get_log_file_name() -> str:
    from datetime import datetime as dt
    log_path = tug.get_app_setting("DEFAULT_LOG_PATH", "")
    r_path = Path(log_path) if log_path else Path().resolve()
    file_name = f"{dt.now():%b %d %H.%M.%S}.log"
    file = r_path / file_name
    return file.as_posix()

def set_logger():
    logger.remove()
    use_logging = int(tug.get_app_setting("SWITCH_ON_LOGGING", 0))
    if not use_logging:
        return

    fmt = "{time:%y-%b-%d %H:%M:%S} | {level} | {module}.{function}({line}): {message}"

    LOG_FILE = get_log_file_name()
    logger.add(LOG_FILE, format=fmt, enqueue=True)
    # logger.add(sys.stderr, format=fmt, enqueue=True)
    logger.info(f'{ag.app_name()=}, {ag.app_version()=}')
    logger.info(f"START =================> {LOG_FILE}")
