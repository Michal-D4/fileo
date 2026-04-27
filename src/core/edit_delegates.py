# from loguru import logger

from PyQt6.QtCore import QEvent, Qt, QTimer, QModelIndex
from PyQt6.QtWidgets import QStyledItemDelegate, QLineEdit

from . import app_globals as ag


class fileEditorDelegate(QStyledItemDelegate):
    """
    The purpose of this delegate:
      - not open editor by the double click event
      - edit filename in the file_list
      - when start editing, select only file name without period and extension
      - edited file name saving depends on the reason for closing editor
    """
    def __init__(self, parent = None) -> None:
        self.curr_index = QModelIndex()
        super().__init__(parent)

    def eventFilter(self, editor, event):
        if event.type() == QEvent.Type.KeyPress:
            key = event.key()
            if key == Qt.Key.Key_Return or key == Qt.Key.Key_Enter:
                # commit data and close editor
                self.commitData.emit(editor)
                self.closeEditor.emit(editor, QStyledItemDelegate.EndEditHint.NoHint)
                ag.file_list.model().set_inserted_row(-1)
                return True
            if key == Qt.Key.Key_Escape:
                # close the editor without committing data, delete new row from model
                # important: closeEditor before cancel_edit
                self.closeEditor.emit(editor, QStyledItemDelegate.EndEditHint.NoHint)
                ag.signals.cancel_edit.emit()
                ag.file_list.model().set_inserted_row(-1)
                return True
        return super().eventFilter(editor, event)

    def editorEvent(self, ev: QEvent, model, option, index) -> bool:
        return ev.type() is QEvent.Type.MouseButtonDblClick

    def setEditorData(self, editor: QLineEdit, index):
        def set_selection():
            try:
                editor.setSelection(0, pos)
            except RuntimeError:
                pass

        self.curr_index = index
        editor.setText(index.data(Qt.ItemDataRole.EditRole))
        pos =  editor.text().rfind('.', 1)
        if pos > 0:
            QTimer.singleShot(25, set_selection)


class folderEditDelegate(QStyledItemDelegate):
    """
    The purpose of this delegate is to switch between
    editing the folder name and editing the folder's tooltip.
    """
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
