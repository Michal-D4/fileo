# import os
# os.environ['QT_FATAL_WARNINGS'] = '1'  # to have traceback in warning
import sys

from loguru import logger

from PyQt6.QtCore import (Qt, pyqtSlot, QItemSelectionModel,
    QLockFile, QDir, )
from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtWidgets import QApplication, QWidget

from . import tug
from .core import app_globals as ag, sho


def run_instance(lock: list) -> bool:
    if tug.config.get('instance_control', False):
        ag.single_instance = int(tug.get_app_setting("SINGLE_INSTANCE", 0))
        logger.info(f'{ag.single_instance=}')
        if ag.single_instance:
            if not lock:
                lock.append(QLockFile(QDir.tempPath() + '/fileo.lock'))
            if not lock[0].tryLock():
                return False

    return True

# @logger.catch           # to have traceback
def start_app(app: QApplication, db_name: str, first_instance: bool):
    from .core.win_win import set_app_icon

    @pyqtSlot(QWidget, QWidget)
    def tab_toggle_focus():
        if app.focusWidget() is ag.dir_list:
            ag.file_list.setFocus()
        else:
            if ag.mode is ag.appMode.FILTER:
                ag.dir_list.selectionModel().selectionChanged.disconnect(ag.filter_dlg.dir_selection_changed)

            ag.dir_list.setFocus()

            sel_model = ag.dir_list.selectionModel()
            selection = sel_model.selection()
            sel_model.select(selection, QItemSelectionModel.SelectionFlag.Clear)
            sel_model.select(selection, QItemSelectionModel.SelectionFlag.Select)
            if ag.mode is ag.appMode.FILTER:
                ag.dir_list.selectionModel().selectionChanged.connect(ag.filter_dlg.dir_selection_changed)

    def set_style():
        styles = tug.prepare_styles(theme_key, to_save=log_qss)
        app.setStyleSheet(styles)
        set_app_icon(app)

    log_qss = tug.config.get("save_prepared_qss", False)
    _, theme_key = tug.get_app_setting(
        "Current Theme", ("Default Theme", "Default_Theme")
    )
    logger.info(f'{theme_key=}')
    try:
        set_style()
    except Exception as e:
        logger.exception(f"styleSheet Error?: {e.args};", exc_info=True)
        return

    main_window = sho.shoWindow(db_name, first_instance)

    main_window.show()

    tab = QShortcut(QKeySequence(Qt.Key.Key_Tab), ag.app)
    tab.activated.connect(tab_toggle_focus)
    ctrl_h = QShortcut(QKeySequence("Ctrl+h"), ag.app)
    ctrl_h.activated.connect(
        lambda: ag.signals_.user_signal.emit("show_recent_files")
    )

    sys.exit(app.exec())

def main(entry_point: str, db_name: str, first_instance: bool):
    app = QApplication([])
    tug.entry_point = entry_point
    tug.set_logger()

    logger.info(f'{ag.app_name()=}, {ag.app_version()=}, {first_instance=}')
    logger.info(f'{entry_point=}')
    logger.info(f'{db_name=}')

    lock = []
    if run_instance(lock):
        start_app(app, db_name, first_instance)
        if lock:
            lock[0].unlock()
