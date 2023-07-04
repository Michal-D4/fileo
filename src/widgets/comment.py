from loguru import logger
from datetime import datetime

from PyQt6.QtCore  import QUrl, pyqtSignal, pyqtSlot, QSize
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import QWidget

from core import icons, app_globals as ag, db_ut
from .ui_comment import Ui_comment

MIN_HEIGHT = 50

class Comment(QWidget):

    delete_note = pyqtSignal(int)
    start_edit = pyqtSignal(int)
    finsih_edit = pyqtSignal(int)   # not iterate all items

    def __init__(self, id: int,
                 modified: int,
                 created: int,
                 parent: QWidget=None) -> None:
        super().__init__(parent)

        self.id = id
        self.modified = datetime.fromtimestamp(modified)
        self.created = datetime.fromtimestamp(created)

        self.visible_height = MIN_HEIGHT
        self.expanded_height = 0
        # logger.info(f'{id=}, {self.visible_height=}')

        self.ui = Ui_comment()

        self.ui.setupUi(self)
        self.ui.edit.setIcon(icons.get_other_icon("toEdit"))
        self.ui.remove.setIcon(icons.get_other_icon("cancel2"))
        self.ui.textBrowser.setOpenLinks(False)

        self.ui.collapse.clicked.connect(self.collapse_item)
        self.ui.edit.clicked.connect(self.edit_note)
        self.ui.remove.clicked.connect(self.remove_note)
        ag.signals_.finish_edit.connect(self.edit_finish)
        self.ui.textBrowser.anchorClicked.connect(self.ref_clicked)

        self.set_collapse_icon(False)

    @pyqtSlot(int)
    def edit_finish(self, id: int):

        logger.info(f'{self.id} == {id}, not iterate all items')
        if self.id == id:
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

    def sizeHint(self) -> QSize:
        return QSize(0, self.visible_height)

    @pyqtSlot(bool)
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

    @pyqtSlot()
    def edit_note(self):
        self.start_edit.emit(self.id)

    @pyqtSlot()
    def remove_note(self):
        self.delete_note.emit(self.id)

    @pyqtSlot(QUrl)
    def ref_clicked(self, href: QUrl):
        tref = href.toString()
        if tref.startswith('http'):
            QDesktopServices.openUrl(href)
