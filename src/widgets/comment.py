from loguru import logger
from datetime import datetime

from PyQt6.QtCore  import QUrl, pyqtSlot, QSize
from PyQt6.QtGui import QDesktopServices, QResizeEvent
from PyQt6.QtWidgets import QWidget

from ..core import icons, app_globals as ag
from .ui_comment import Ui_comment

MIN_HEIGHT = 50
TIME_FORMAT = "%Y-%m-%d %H:%M"


class Comment(QWidget):

    def __init__(self, id: int=0,
                 modified: int=0,
                 created: int=0,
                 parent: QWidget=None) -> None:
        super().__init__(parent)

        self.id = id
        self.modified = datetime.fromtimestamp(modified)
        self.created = datetime.fromtimestamp(created)
        self.text = ''

        self.visible_height = MIN_HEIGHT
        self.expanded_height = 0
        logger.info(f'{id=}, {self.visible_height=}')

        self.ui = Ui_comment()

        self.ui.setupUi(self)
        self.ui.edit.setIcon(icons.get_other_icon("toEdit"))
        self.ui.remove.setIcon(icons.get_other_icon("cancel2"))
        self.ui.created.setText(f'created: {self.created.strftime(TIME_FORMAT)}')
        self.ui.modified.setText(f'modified: {self.modified.strftime(TIME_FORMAT)}')
        self.ui.textBrowser.setOpenLinks(False)

        self.ui.collapse.clicked.connect(self.collapse_item)
        self.ui.edit.clicked.connect(self.edit_note)
        self.ui.remove.clicked.connect(self.remove_note)
        self.ui.textBrowser.anchorClicked.connect(self.ref_clicked)

        self.set_collapse_icon(False)

    def get_note_text(self) -> str:
        return self.ui.textBrowser.toMarkdown()

    def set_note_text(self, note: str):
        self.text = note

    def set_browser_text(self):
        self.ui.textBrowser.setMarkdown(self.text)
        self.set_height_by_text()
        self.updateGeometry()

    def set_height_by_text(self):
        self.ui.textBrowser.document().setTextWidth(self.ui.textBrowser.width())
        size = self.ui.textBrowser.document().size().toSize()
        self.visible_height = size.height() + self.ui.item_header.height()

    def set_note_id(self, id: int):
        self.id = id

    def get_note_id(self) -> int:
        return self.id

    def set_created_date(self, created: int):
        self.created = datetime.fromtimestamp(created)
        self.ui.created.setText(f'created: {self.created.strftime(TIME_FORMAT)}')

    def set_modified_date(self, modified: int):
        self.modified = datetime.fromtimestamp(modified)
        self.ui.modified.setText(f'modified: {self.modified.strftime(TIME_FORMAT)}')

    def sizeHint(self) -> QSize:
        return QSize(0, self.visible_height)

    @pyqtSlot(bool)
    def collapse_item(self, state: bool):
        if state:
            self.expanded_height = self.visible_height
            self.visible_height = self.ui.item_header.height()
            self.ui.textBrowser.hide()
        else:
            self.visible_height = self.expanded_height
            self.expanded_height = 0
            self.ui.textBrowser.show()
        self.set_collapse_icon(state)

    def set_collapse_icon(self, collapse: bool):
        self.ui.collapse.setIcon(
            icons.get_other_icon("right") if collapse
            else icons.get_other_icon("down")
        )

    @pyqtSlot()
    def edit_note(self):
        ag.signals_.start_edit_note.emit(self.id)

    @pyqtSlot()
    def remove_note(self):
        ag.signals_.delete_note.emit(self.id)

    @pyqtSlot(QUrl)
    def ref_clicked(self, href: QUrl):
        tref = href.toString()
        if tref.startswith('http'):
            QDesktopServices.openUrl(href)

    def resizeEvent(self, a0: QResizeEvent) -> None:
        self.set_browser_text()
        return super().resizeEvent(a0)
