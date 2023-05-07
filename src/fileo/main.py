import os, sys

from loguru import logger

# os.environ['PYTHONBREAKPOINT'] = 'web_pdb.set_trace'
# from PyQt6.QtCore import pyqtRemoveInputHook
# pyqtRemoveInputHook()
os.environ['PYTHONBREAKPOINT'] = '0'

from PyQt6.QtWidgets import QApplication

from .core import utils
from .core.sho import shoWindow


def main():
    app = QApplication([])
    # logger.remove()
    # # fmt = "{time:%b-%d %H:%M:%S} | {level:6} | {module}.{function}({line}): {message}"
    # fmt = "{time:%b-%d %H:%M:%S} | {module}.{function}({line}): {message}"
    # from datetime import datetime as dt
    # file_name = f"fill-{dt.now():%b-%d-%H}.log"
    # # file_name = "sys.stderr"
    # if file_name == "sys.stderr":
    #     logger.add(sys.stderr, format=fmt)
    # else:
    #     logger.add(file_name, format=fmt)
    # logger.info("START ==============================>")

    thema_name = "default"

    try:
        utils.apply_style(app, thema_name, to_save=True)
    except KeyError as e:
        logger.info(f"KeyError: {e.args}; >>> check you qss parameters file {thema_name}.param")
        return

    main_window = shoWindow()

    main_window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
