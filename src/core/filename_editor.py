from PyQt6.QtCore import QEvent
from PyQt6.QtWidgets import QStyledItemDelegate


class fileEditorDelegate(QStyledItemDelegate):
    '''
    The purpose of this delegate is to prevent editing of the file name with double-click event.
    The file must be opened by the double click event
    '''
    def __init__(self, parent = None) -> None:
        super().__init__(parent)

    def editorEvent(self, event: QEvent, model, option, index) -> bool:
        return event.type() is QEvent.Type.MouseButtonDblClick
