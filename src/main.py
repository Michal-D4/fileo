# import os
# os.environ['QT_FATAL_WARNINGS'] = '1'  # to have traceback in warning
import sys

from loguru import logger

from PyQt6.QtCore import Qt, pyqtSlot, QItemSelectionModel
from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtWidgets import QApplication, QWidget

from . import tug
from .core import app_globals as ag, sho


# @logger.catch           # to have traceback
def start_app(app: QApplication, db_name: str, first_instance: bool):
    from .core.win_win import set_app_icon

    @pyqtSlot(QWidget, QWidget)
    def tab_toggle_focus():
        def reset_dir_selection():
            selection = sel_model.selection()
            sel_model.select(selection, QItemSelectionModel.SelectionFlag.Clear)
            sel_model.select(selection, QItemSelectionModel.SelectionFlag.Select)
        if app.focusWidget() is ag.dir_list:
            ag.file_list.setFocus()
        else:
            sel_model = ag.dir_list.selectionModel()
            if ag.mode is ag.appMode.FILTER:
                sel_model.selectionChanged.disconnect(ag.filter_dlg.dir_selection_changed)

            ag.dir_list.setFocus()
            reset_dir_selection()

            if ag.mode is ag.appMode.FILTER:
                sel_model.selectionChanged.connect(ag.filter_dlg.dir_selection_changed)

    def set_style():
        styles = tug.prepare_styles(theme_key, to_save=log_qss)
        app.setStyleSheet(styles)
        set_app_icon(app)

    log_qss = tug.config.get("save_prepared_qss", False)
    _, theme_key = tug.get_app_setting(
        "Current Theme", ("Default Theme", "Default_Theme")
    )

    try:
        set_style()
    except Exception as e:
        logger.exception(f"styleSheet Error?: {e.args};", exc_info=True)
        return

    main_window = sho.shoWindow(db_name, first_instance)

    main_window.show()

    tab = QShortcut(QKeySequence(Qt.Key.Key_Tab), ag.app)
    tab.activated.connect(tab_toggle_focus)

    sys.exit(app.exec())

def main(entry_point: str, db_name: str, first_instance: bool):
    tug.set_config()
    app = QApplication([])
    tug.entry_point = entry_point
    tug.set_logger(first_instance)

    logger.info(f'{ag.app_name()=}, {ag.app_version()=}, {first_instance=}')
    logger.info(f'{entry_point=}')
    logger.info(f'{db_name=}')

    start_app(app, db_name, first_instance)
