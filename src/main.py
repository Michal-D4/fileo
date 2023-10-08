import sys

from loguru import logger
from pathlib import Path

from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtWidgets import QApplication, QWidget

from .core import utils, app_globals as ag, iman
from .core.sho import shoWindow

if sys.platform.startswith("win"):
    from .core import win_win as win_activate
elif sys.platform.startswith("linux"):
    from .core import linux_win as win_activate
else:
    raise ImportError(f"doesn't support {sys.platform} system")


app: QApplication = None

@pyqtSlot(QWidget, QWidget)
def tab_pressed():
    global app
    old = app.focusWidget()
    if old is ag.dir_list:
        ag.file_list.setFocus()
    else:
        ag.dir_list.setFocus()

def set_logger():
    logger.remove()
    use_logging = int(utils.get_app_setting("SWITCH_ON_LOGGING", 0))
    if not use_logging:
        return

    fmt = "{time:%y-%b-%d %H:%M:%S} | {module}.{function}({line}): {message}"

    std_err = int(utils.get_app_setting("LOGGING_TO_STDERR", 0))
    if std_err:
        logger.add(sys.stderr, format=fmt)
    else:
        from datetime import datetime as dt
        log_path = utils.get_app_setting("DEFAULT_LOG_PATH", "")
        r_path = Path(log_path) if log_path else Path().resolve()
        file_name = f"{dt.now():%b %d %H.%M.%S}.log"
        file = r_path / file_name

        logger.add(file.as_posix(), format=fmt)
    logger.info(f'{ag.app_name()=}, {ag.app_version()=}')
    logger.info("START =================>")

def instance_control(db_name: str):
    global app
    app = QApplication([])

    pid = iman.new_app_instance()

    ag.single_instance = int(utils.get_app_setting("SINGLE_INSTANCE", 0))
    logger.info(f'{db_name}, {pid=}, {ag.single_instance=}')
    if pid:
        if ag.single_instance:
            win_activate.activate(pid)
            iman.app_instance_closed()

            sys.exit(0)
        else:
            ag.db.conn = None
            ag.db.path = db_name
            ag.db.restore = bool(db_name)
            logger.info(f'ag.DB: {ag.db!r}')


def start_app():
    thema_name = "default"
    try:
        log_qss = int(utils.get_app_setting("LOG_QSS", 0))
        utils.apply_style(app, thema_name, to_save=log_qss)
    except KeyError as e:
        # message for developers
        logger.info(f"KeyError: {e.args}; >>> check you qss parameters file {thema_name}.param")
        return

    main_window = shoWindow()

    main_window.show()
    tab = QShortcut(QKeySequence(Qt.Key.Key_Tab), ag.app)
    tab.activated.connect(tab_pressed)

    sys.exit(app.exec())


def main(entry_point: str, db_name: str):
    set_logger()
    tmp = Path(entry_point).resolve()
    logger.info(entry_point)
    if getattr(sys, "frozen", False):
        ag.entry_point = tmp.as_posix()   # str
    else:
        ag.entry_point = tmp.name

    instance_control(db_name)

    start_app()
