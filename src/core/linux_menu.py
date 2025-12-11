from PyQt6.QtCore import Qt, QDataStream, QIODevice, QCoreApplication
from PyQt6.QtGui import QDropEvent
from PyQt6.QtWidgets import QMenu

from . import app_globals as ag

def choose_drop_action(e: QDropEvent):
    if use_action_menu(e):
        action_menu(e)

def use_action_menu(e: QDropEvent) -> bool:
    if e.modifiers() & Qt.KeyboardModifier.ShiftModifier:
        e.setDropAction(Qt.DropAction.MoveAction)
        return False
    if e.modifiers() & Qt.KeyboardModifier.ControlModifier:
        e.setDropAction(Qt.DropAction.CopyAction)
        return False
    if e.mimeData().hasFormat(ag.mimeType.folders.value):
        e.setDropAction(Qt.DropAction.CopyAction)
        return True
    if e.mimeData().hasFormat(ag.mimeType.files_in.value):
        data = e.mimeData()
        files_data = data.data(ag.mimeType.files_in.value)
        stream = QDataStream(files_data, QIODevice.OpenModeFlag.ReadOnly)
        pid_drag_from = stream.readInt()
        if QCoreApplication.applicationPid() == pid_drag_from:   # mimeType.files_in
            e.setDropAction(Qt.DropAction.CopyAction)
            return True
    return False

def action_menu(e: QDropEvent):
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
            return
        if act.text().startswith('Move'):
            e.setDropAction(Qt.DropAction.MoveAction)
            return
    e.setDropAction(Qt.DropAction.IgnoreAction)
