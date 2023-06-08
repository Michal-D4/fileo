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
    """
    pos = e.position().toPoint()
    if (ag.drop_button == Qt.MouseButton.RightButton and
        (ag.mode is ag.appMode.DIR or
         not e.mimeData().hasFormat(ag.mimeType.files.value)
        )):
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
