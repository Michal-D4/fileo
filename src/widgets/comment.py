from loguru import logger
from typing import List
from PyQt6 import QtCore, QtGui
from PyQt6.QtWidgets import QWidget

from core import icons, app_globals as ag
from .ui_comment import Ui_comment

MIN_HEIGHT = 50

class Comment(QWidget):

    del_note_signal = QtCore.pyqtSignal(int)
    start_edit = QtCore.pyqtSignal(int)

    def __init__(self, id: int, parent: QWidget=None) -> None:
        super().__init__(parent)

        self.ui = Ui_comment()

        self.ui.setupUi(self)
        self.ui.edit.setIcon(icons.get_other_icon("toEdit"))
        self.ui.remove.setIcon(icons.get_other_icon("cancel2"))
        self.ui.textEdit.hide()

        self.visible_height = MIN_HEIGHT
        self.expanded_height = 0
        # logger.info(f'{id=}, {self.visible_height=}')

        self.id = id

        self.ui.collapse.clicked.connect(self.collapse_item)
        self.ui.edit.clicked.connect(self.edit_note)
        self.ui.remove.clicked.connect(self.remove_note)

        ag.signals_.finish_edit.connect(self.edit_finish)
        self.set_collapse_icon(False)

    @QtCore.pyqtSlot(int)
    def edit_finish(self, id: int):
        if self.id == id:
            self.ui.edit.setEnabled(True)
            self.set_note_text(self.ui.textEdit.toPlainText())
            self.ui.textBrowser.show()
            self.ui.textEdit.hide()

    def set_note_text(self, note: str):
        self.ui.textBrowser.setMarkdown(note)
        self.set_height_by_text()
        self.updateGeometry()

    def set_height_by_text(self):
        size = self.ui.textBrowser.document().size().toSize()
        self.visible_height = size.height() + self.ui.item_header.height()

    def set_note_id(self, id: int):
        self.id = id

    def get_note_id(self) -> int:
        return self.id

    def sizeHint(self) -> QtCore.QSize:
        return QtCore.QSize(0, self.visible_height)

    @QtCore.pyqtSlot(bool)
    def collapse_item(self, state: bool):
        active = self.ui.textBrowser if self.ui.edit.isEnabled() else self.ui.textEdit

        if state:
            self.expanded_height = self.height()
            self.visible_height -= active.height()
            active.hide()
        else:
            self.visible_height = self.expanded_height
            self.expanded_height = 0
            active.show()
        self.set_collapse_icon(state)

    def set_collapse_icon(self, collapse: bool):
        self.ui.collapse.setIcon(
            icons.get_other_icon("right") if collapse
            else icons.get_other_icon("down")
        )

    @QtCore.pyqtSlot()
    def edit_note(self):
        self.ui.edit.setEnabled(False)
        self.ui.textBrowser.hide()
        self.ui.textEdit.setMinimumHeight(self.ui.textBrowser.height()+20)
        self.ui.textEdit.setText(self.ui.textBrowser.toPlainText())
        self.ui.textEdit.show()
        self.start_edit.emit(self.id)
        self.visible_height = self.height()

    @QtCore.pyqtSlot()
    def remove_note(self):
        self.del_note_signal.emit(self.id)