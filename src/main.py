# import os
# os.environ['QT_FATAL_WARNINGS'] = '1'  # to have traceback in warning
import sys

from loguru import logger

from PyQt6.QtCore import Qt, pyqtSlot, QLockFile, QDir
from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtWidgets import QApplication

from . import tug
from .core import app_globals as ag
from .core.sho import shoWindow

# @logger.catch           # to have traceback
def start_app(app: QApplication, db_name: str, first_instance: bool):
    from .core.win_win import set_app_icon

    @pyqtSlot()
    def tab_toggle_focus():
        if app.focusWidget() is ag.dir_list:
            ag.file_list.setFocus(Qt.FocusReason.TabFocusReason)
        else:
            ag.dir_list.setFocus(Qt.FocusReason.TabFocusReason)
            ag.dir_list.update()

    def set_style():
        styles = tug.prepare_styles(theme_key, to_save=False)
        app.setStyleSheet(styles)
        set_app_icon(app)

    if first_instance:
        lock_file = QLockFile(QDir.tempPath() + '/fileo.lock')
        lock_file.setStaleLockTime(0)
        if not lock_file.tryLock(5):      # 5 milliseconds
            logger.info(f'{lock_file.error()=}')
            if lock_file.error() is QLockFile.LockError.LockFailedError:
                sys.exit(0)
        #     logger.info('after lock_file.tryLock -- never run')
        # logger.info('after lock_file.tryLock -- only in success lock')

    theme_key = tug.get_app_setting("CurrentTheme", "Default_Theme")
    try:
        set_style()
    except Exception as e:
        logger.exception(f"styleSheet Error?: {e.args};", exc_info=True)
        return

    main_window = shoWindow(db_name, first_instance)
    main_window.show()

    tab = QShortcut(QKeySequence(Qt.Key.Key_Tab), ag.app)
    tab.activated.connect(tab_toggle_focus)

    sys.exit(app.exec())

def main(entry_point: str, db_name: str, first_instance: bool):
    app = QApplication([])
    tug.entry_point = entry_point
    tug.set_logger(first_instance)

    logger.info(f'{ag.app_name()=}, {ag.app_version()=}, {first_instance=}')
    logger.info(f'{entry_point=}')
    logger.info(f'{db_name=}')

    start_app(app, db_name, first_instance)
