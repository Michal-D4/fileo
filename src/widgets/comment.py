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
        self.ui.textEdit.hide()

        self.height_ = MIN_HEIGHT
        self.id = id

        self.ui.collapse.clicked.connect(self.collapse_item)
        self.ui.edit.clicked.connect(self.edit_note)
        self.ui.remove.clicked.connect(self.remove_note)

        ag.signals_.finish_edit.connect(self.edit_finish)
        self.collapse_item(False)

    @QtCore.pyqtSlot(int)
    def edit_finish(self, id: int):
        if self.id == id:
            self.ui.textBrowser.setMarkdown(self.ui.textEdit.toPlainText())
            self.ui.textBrowser.show()
            self.ui.textEdit.hide()

    def set_note_text(self, note: str):
        self.ui.textBrowser.setMarkdown(note)
        size = self.ui.textBrowser.document().size().toSize()
        self.height_ = size.height() + self.ui.item_header.height()
        logger.info(f'{size=}')
        self.updateGeometry()

    def set_note_id(self, id: int):
        self.id = id

    def get_note_id(self) -> int:
        return self.id

    def set_height(self, height: int):
        self.height_ = height
        self.updateGeometry()

    def sizeHint(self) -> QtCore.QSize:
        return QtCore.QSize(0, self.height_)

    def get_heigh(self) -> int:
        return self.height_

    @QtCore.pyqtSlot(bool)
    def collapse_item(self, state: bool):
        if state:
            self.ui.textBrowser.hide()
            self.ui.collapse.setIcon(icons.get_other_icon("right"))
        else:
            self.ui.textBrowser.show()
            self.ui.collapse.setIcon(icons.get_other_icon("down"))

    @QtCore.pyqtSlot()
    def edit_note(self):
        self.ui.textBrowser.hide()
        self.ui.textEdit.setMinimumHeight(self.ui.textBrowser.height()+20)
        self.ui.textEdit.show()
        self.ui.textEdit.setText(self.ui.textBrowser.toPlainText())
        self.start_edit.emit(self.id)

    @QtCore.pyqtSlot()
    def remove_note(self):
        self.del_note_signal.emit(self.id)