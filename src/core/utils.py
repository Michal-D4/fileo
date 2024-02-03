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
