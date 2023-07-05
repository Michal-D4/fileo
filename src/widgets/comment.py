from loguru import logger
from datetime import datetime

from PyQt6.QtCore  import QUrl, pyqtSignal, pyqtSlot, QSize
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import QWidget

from ..core import icons, app_globals as ag, db_ut
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
        nnote = note.replace(r'\n', '<br>')
        self.ui.textBrowser.setMarkdown(nnote)
        logger.info(nnote)
        self.set_height_by_text()
        self.updateGeometry()

    def set_height_by_text(self):
        size = self.ui.textBrowser.document().size().toSize()
        logger.info(f'{size=}, {size.height()=} {self.ui.textBrowser.toMarkdown()}')
        self.visible_height = size.height() + self.ui.item_header.height()

    def set_note_id(self, id: int):
        self.id = id

    def get_note_id(self) -> int:
        return self.id

    def set_created(self, created: int):
        self.created = datetime.fromtimestamp(created)

    def set_modified(self, modified: int):
        self.modified = datetime.fromtimestamp(modified)

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
        ag.signals_.start_edit_note.emit(self.id)

    @pyqtSlot()
    def remove_note(self):
        ag.signals_.delete_note.emit(self.id)

    @pyqtSlot(QUrl)
    def ref_clicked(self, href: QUrl):
        tref = href.toString()
        if tref.startswith('http'):
            QDesktopServices.openUrl(href)
