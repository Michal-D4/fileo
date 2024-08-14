from loguru import logger

from PyQt6.QtCore import QEvent, Qt
from PyQt6.QtWidgets import QStyledItemDelegate, QLineEdit


class fileEditorDelegate(QStyledItemDelegate):
    '''
    The purpose of this delegate is to prevent editing of the file name with double-click event.
    The file must be opened by the double click event
    '''
    def __init__(self, parent = None) -> None:
        super().__init__(parent)

    def editorEvent(self, event: QEvent, model, option, index) -> bool:
        return event.type() is QEvent.Type.MouseButtonDblClick


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

    def createEditor(self, parent, styleOption, index):
        editor = QLineEdit(parent)
        return editor

    def setEditorData(self, editor, index):
        logger.info(f'data_role: {self.data_role}')
        editor.setText(index.data(self.data_role))

    def setModelData(self, editor, model, index):
        logger.info(f'data: {editor.text()}, role: {self.data_role}')
        model.setData(index, editor.text(), self.data_role)
        folderEditDelegate.data_role = Qt.ItemDataRole.EditRole
