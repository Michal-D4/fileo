import os, sys

from loguru import logger

# os.environ['PYTHONBREAKPOINT'] = 'web_pdb.set_trace'
# from PyQt6.QtCore import pyqtRemoveInputHook
# pyqtRemoveInputHook()
os.environ['PYTHONBREAKPOINT'] = '0'

from PyQt6.QtCore import Qt, pyqtSlot, QLockFile, QDir
from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtWidgets import QApplication, QWidget

from .core import utils, app_globals as ag
from .core.sho import shoWindow

app: QApplication = None

def app_name() -> str:
    return "fileo"

def app_version() -> str:
    """
    if it changes then also change in "pyproject.toml" file
    what the shit is this versioning support API
    it's easier to hardcode it everywhere
    """
    return '0.9.0'

@pyqtSlot(QWidget, QWidget)
def tab_pressed():
    global app
    old = app.focusWidget()
    if old is ag.dir_list:
        ag.file_list.setFocus()
    else:
        ag.dir_list.setFocus()

def set_logger(file):
    logger.remove()
    # fmt = "{time:%b-%d %H:%M:%S} | {level:6} | {module}.{function}({line}): {message}"
    fmt = "{time:%b-%d %H:%M:%S} | {module}.{function}({line}): {message}"
    file_name = file
    if file_name == "sys.stderr":
        logger.add(sys.stderr, format=fmt)
    else:
        logger.add(file_name, format=fmt)
    logger.info("START ==============================>")
    logger.info(f'{app_name()=}, {app_version()=}')

def main():
    # from datetime import datetime as dt
    # file_name = f"fill-{dt.now():%b-%d-%H}.log"
    # file_name = "sys.stderr"
    # set_logger(file_name)

    try:
        lock_file = QLockFile(QDir.tempPath() + '/' + app_name() + '.lock')
        if not lock_file.tryLock():
            sys.exit(0)

        global app
        app = QApplication([])


        try:
            thema_name = "default"
            utils.apply_style(app, thema_name, to_save=True)
        except KeyError as e:
            # message for developers
            logger.info(f"KeyError: {e.args}; >>> check you qss parameters file {thema_name}.param")
            return

        main_window = shoWindow()

        main_window.show()
        tab = QShortcut(QKeySequence(Qt.Key.Key_Tab), ag.app)
        tab.activated.connect(tab_pressed)

        sys.exit(app.exec())
    finally:
        lock_file.unlock()


if __name__ == "__main__":
    main()
