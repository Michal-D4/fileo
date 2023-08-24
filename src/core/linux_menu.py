from loguru import logger

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDropEvent
from PyQt6.QtWidgets import QMenu


from . import app_globals as ag

def choose_drop_action(e: QDropEvent):
    """
    MoveAction can be used in the following cases
    1 - to move folders, always
    2 - to move files in case of ag.appMode.DIR
    Otherwise, only CopyAction can be used
    The menu appears if both Actions can be used
    and KeyboardModifier is not used.
    """
    if (ag.mode is ag.appMode.DIR or
        not e.mimeData().hasFormat(ag.mimeType.files_in.value)):
        if not has_modifier(e):
            use_menu(e)
    else:
        e.setDropAction(Qt.DropAction.CopyAction)

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
