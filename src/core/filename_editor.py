from PyQt6.QtCore import QEvent
from PyQt6.QtWidgets import QItemDelegate


class fileEditorDelegate(QItemDelegate):
    '''
    the purpose of this delegate is to refuse editing with a double click
    file must be opened with this event (double click)
    '''
    def __init__(self, parent = None) -> None:
        super().__init__(parent)

    def editorEvent(self, event: QEvent, model, option, index) -> bool:
        return event.type() is QEvent.Type.MouseButtonDblClick
