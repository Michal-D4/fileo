from loguru import logger

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDropEvent
from PyQt6.QtWidgets import QMenu

from . import app_globals as ag

drop_button = 0

def choose_drop_action(e: QDropEvent):
    """
    The default action ic Copy,
    Right button is used to choose action from menu
    """
    if drop_button == Qt.MouseButton.RightButton:
        pos = e.position().toPoint()
        menu = QMenu(ag.app)
        menu.addAction('Copy')
        menu.addAction('Move')
        act = menu.exec(ag.app.mapToGlobal(pos))
        if act:
            if act.text().startswith('Copy'):
                e.setDropAction(Qt.DropAction.CopyAction)
            elif act.text().startswith('Move'):
                e.setDropAction(Qt.DropAction.MoveAction)
        else:
            e.setDropAction(Qt.DropAction.IgnoreAction)
            e.ignore()
    else:
        e.setDropAction(Qt.DropAction.CopyAction)
