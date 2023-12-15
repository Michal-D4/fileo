import qss
import sys

from loguru import logger
from pathlib import Path

from PyQt6.QtCore import Qt, pyqtSlot, QCoreApplication, QTimer, QItemSelectionModel
from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtWidgets import QApplication, QWidget

from .core import utils, app_globals as ag, iman
from .core.sho import shoWindow

timer = None

if sys.platform.startswith("win"):
    from .core.win_win import activate, win_icons
elif sys.platform.startswith("linux"):
    from .core.linux_win import activate, win_icons
else:
    raise ImportError(f"doesn't support {sys.platform} system")


def run_instance(db_name: str='') -> bool:
    if qss.config['instance_control']:
        iman.PORT = int(utils.get_app_setting('PORT_NUMBER', 10010))
        global timer
        ag.PID = QCoreApplication.applicationPid()
        pid = iman.new_app_instance()
        logger.info(f'{pid=}')
        if pid:
            ag.single_instance = int(utils.get_app_setting("SINGLE_INSTANCE", 0))
            if ag.single_instance:
                activate(pid)
                iman.app_instance_close()
                return False

    ag.db.conn = None
    ag.db.path = db_name if db_name != '-' else ''
    ag.db.restore = bool(db_name)

    return True

@pyqtSlot()
def is_active_message():
    iman.send_message()

def start_app(app: QApplication):
    @pyqtSlot(QWidget, QWidget)
    def tab_pressed():
        old = app.focusWidget()
        if old is ag.dir_list:
            ag.file_list.setFocus()
        else:
            ag.dir_list.setFocus()
            idx = ag.dir_list.currentIndex()
            sel_model = ag.dir_list.selectionModel()
            cur_selection = sel_model.selection()
            sel_model.select(cur_selection, QItemSelectionModel.SelectionFlag.Clear)
            sel_model.select(cur_selection, QItemSelectionModel.SelectionFlag.Select)

    thema_name = "default"
    try:
        log_qss = int(utils.get_app_setting("LOG_QSS", 0))
        utils.apply_style(app, thema_name, to_save=log_qss)
        win_icons()
    except KeyError as e:
        # message for developers
        logger.info(f"KeyError: {e.args}; >>> check you qss parameters file {thema_name}.param")
        return

    main_window = shoWindow()

    main_window.show()
    tab = QShortcut(QKeySequence(Qt.Key.Key_Tab), ag.app)
    tab.activated.connect(tab_pressed)

    if qss.config['instance_control']:
        timer = QTimer(ag.app)
        timer.timeout.connect(is_active_message)
        timer.setInterval(ag.TIME_CHECK * 1000)
        timer.start()

    sys.exit(app.exec())


def main(entry_point: str, db_name: str):
    app = QApplication([])

    utils.set_logger()
    logger.info(f'{db_name=}')

    tmp = Path(entry_point).resolve()
    if getattr(sys, "frozen", False):
        ag.entry_point = tmp.as_posix()   # str
    else:
        ag.entry_point = tmp.name

    if run_instance(db_name):
        logger.info(f'>>> {ag.PID} {entry_point=}, {ag.entry_point=}')
        start_app(app)
