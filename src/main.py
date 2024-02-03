import sys

from loguru import logger
from pathlib import Path

from PyQt6.QtCore import Qt, pyqtSlot, QItemSelectionModel, QLockFile, QDir
from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtWidgets import QApplication, QWidget

from src import tug
from .core import utils, app_globals as ag
from .core.sho import shoWindow

lock_file = None

def run_instance(db_name: str='') -> bool:
    if tug.config.get('instance_control', False):
        ag.single_instance = int(tug.get_app_setting("SINGLE_INSTANCE", 0))
        if ag.single_instance:
            global lock_file
            lock_file = QLockFile(QDir.tempPath() + '/fileo.lock')
            if not lock_file.tryLock():
                return False

    ag.db.conn = None
    ag.db.path = db_name if db_name != '-' else ''
    ag.db.restore = bool(db_name)

    return True

# @logger.catch
def start_app(app: QApplication):
    from .core.win_win import set_app_icon

    thema_name = "default"
    try:
        log_qss = int(tug.get_app_setting("LOG_QSS", 0))
        styles = tug.prepare_styles(thema_name, to_save=log_qss)
        app.setStyleSheet(styles)
        set_app_icon(app)
    except KeyError as e:
        # message for developers
        logger.info(f"KeyError: {e.args}; >>> check you qss parameters file {thema_name}.param")
        # logger.exception(f"KeyError: {e.args};", exc_info=True)
        return

    main_window = shoWindow()

    main_window.show()

    @pyqtSlot(QWidget, QWidget)
    def tab_pressed():
        old = app.focusWidget()
        if old is ag.dir_list:
            ag.file_list.setFocus()
        else:
            ag.dir_list.setFocus()

            sel_model = ag.dir_list.selectionModel()
            cur_selection = sel_model.selection()
            sel_model.select(cur_selection, QItemSelectionModel.SelectionFlag.Clear)
            sel_model.select(cur_selection, QItemSelectionModel.SelectionFlag.Select)

    tab = QShortcut(QKeySequence(Qt.Key.Key_Tab), ag.app)
    tab.activated.connect(tab_pressed)
    ctrl_h = QShortcut(QKeySequence("Ctrl+h"), ag.app)
    ctrl_h.activated.connect(
        lambda: ag.signals_.user_signal.emit("show_recent_files")
    )

    sys.exit(app.exec())

def set_entry_point(entry_point: str):
    tmp = Path(entry_point).resolve()
    if getattr(sys, "frozen", False):
        ag.entry_point = tmp.as_posix()   # str
    else:
        ag.entry_point = tmp.name

def main(entry_point: str, db_name: str):
    app = QApplication([])

    logger.info(f'{ag.app_name()=}, {ag.app_version()=}')
    logger.info(f'{entry_point=}, {db_name=}')

    if run_instance(db_name):
        set_entry_point(entry_point)
        logger.info(f'>>> {entry_point=}, {ag.entry_point=}')
        start_app(app)
        global lock_file
        lock_file.unlock()
