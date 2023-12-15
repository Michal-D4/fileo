from loguru import logger

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDropEvent
from PyQt6.QtWidgets import QMenu


from . import app_globals as ag

def choose_drop_action(e: QDropEvent):
    if not has_modifier(e):
        use_menu(e)

def has_modifier(e: QDropEvent) -> bool:
    if e.modifiers() is Qt.KeyboardModifier.ShiftModifier:
        e.setDropAction(Qt.DropAction.MoveAction)
        return True
    if e.modifiers() is Qt.KeyboardModifier.ControlModifier:
        e.setDropAction(Qt.DropAction.CopyAction)
        return True
    return False

def use_menu(e: QDropEvent):
    pos = e.position().toPoint()
    menu = QMenu(ag.app)
    menu.addAction('Move\tShift')
    menu.addAction('Copy\tCtrl')
    menu.addSeparator()
    menu.addAction('Cancel\tEsc')
    act = menu.exec(ag.app.mapToGlobal(pos))
    if act:
        if act.text().startswith('Copy'):
            e.setDropAction(Qt.DropAction.CopyAction)
        elif act.text().startswith('Move'):
            e.setDropAction(Qt.DropAction.MoveAction)
    else:
        e.setDropAction(Qt.DropAction.IgnoreAction)
        e.ignore()
