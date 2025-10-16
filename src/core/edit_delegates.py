# from loguru import logger

from PyQt6.QtCore import QEvent, Qt, QTimer
from PyQt6.QtWidgets import QStyledItemDelegate, QLineEdit


class fileEditorDelegate(QStyledItemDelegate):
    '''
    The purpose of this delegate is to prevent editing of the file name with double-click event.
    The file must be opened by the double click event
    Another purpose: when start editing, select only file name without period and extension.
    '''
    def __init__(self, parent = None) -> None:
        super().__init__(parent)

    def editorEvent(self, event: QEvent, model, option, index) -> bool:
        return event.type() is QEvent.Type.MouseButtonDblClick

    def setEditorData(self, editor: QLineEdit, index):
        def set_selection():
            try:
                editor.setSelection(0, pos)
            except RuntimeError:
                pass

        editor.setText(index.data(Qt.ItemDataRole.EditRole))
        pos =  editor.text().rfind('.', 1)
        if pos > 0:
            QTimer.singleShot(25, set_selection)

class folderEditDelegate(QStyledItemDelegate):
    '''
    The purpose of this delegate is to switch editing of
    folder name - and tooltip to folder name.
    '''
    data_role = Qt.ItemDataRole.EditRole

    def __init__(self, parent = None) -> None:
        super().__init__(parent)

    @classmethod
    def set_tooltip_role(cls):
        folderEditDelegate.data_role = Qt.ItemDataRole.ToolTipRole

    def setEditorData(self, editor, index):
        editor.setText(index.data(self.data_role))

    def setModelData(self, editor, model, index):
        model.setData(index, editor.text(), self.data_role)
        folderEditDelegate.data_role = Qt.ItemDataRole.EditRole
