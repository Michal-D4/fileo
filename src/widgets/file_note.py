from loguru import logger
from datetime import datetime
from pathlib import Path

from PyQt6.QtCore  import Qt, QUrl, pyqtSlot, QSize, QPoint
from PyQt6.QtGui import QDesktopServices, QResizeEvent
from PyQt6.QtWidgets import QWidget, QApplication

from ..core import app_globals as ag, db_ut
from .ui_file_note import Ui_fileNote
from src import tug

MIN_HEIGHT = 50
TIME_FORMAT = "%Y-%m-%d %H:%M"


class fileNote(QWidget):

    def __init__(self,
                 note_file_id: int = 0,  # file_id from filenotes table, find by hash
                 note_id: int=0,
                 modified: int=0,
                 created: int=0,
                 file_id: int=0,         # current file_id in file_list
                 parent: QWidget=None) -> None:
        super().__init__(parent)

        self.file_id = file_id if file_id else note_file_id
        self.id = note_id
        self.note_file_id = note_file_id
        self.collapsed = False

        self.modified = datetime.fromtimestamp(modified)
        self.created = datetime.fromtimestamp(created)
        self.text = ''

        self.visible_height = MIN_HEIGHT
        self.expanded_height = 0

        self.ui = Ui_fileNote()

        self.ui.setupUi(self)
        self.ui.edit.setIcon(tug.get_icon("toEdit"))
        self.ui.remove.setIcon(tug.get_icon("cancel2"))
        self.ui.created.setText(f'created: {self.created.strftime(TIME_FORMAT)}')
        self.ui.modified.setText(f'modified: {self.modified.strftime(TIME_FORMAT)}')
        self.ui.textBrowser.setOpenLinks(False)
        self.ui.textBrowser.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.ui.collapse.clicked.connect(self.toggle_collapse)
        self.ui.edit.clicked.connect(self.edit_note)
        self.ui.remove.clicked.connect(self.remove_note)
        self.ui.textBrowser.anchorClicked.connect(self.ref_clicked)

        self.set_collapse_icon(False)

        self.ui.textBrowser.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.ui.textBrowser.customContextMenuRequested.connect(self.context_menu)

    @pyqtSlot(QPoint)
    def context_menu(self, pos: QPoint):
        def copy_link():
            QApplication.clipboard().setText(self.ui.textBrowser.anchorAt(pos))

        def read_note_file(pp: Path):
            with open(pp) as ff:
                return ff.read()

        def save_notes_to_file():
            def save_note():
                if link in txt:
                    return
                mod_ = datetime.fromtimestamp(md)
                cre_ = datetime.fromtimestamp(cr)
                fn.write('\n***\n')
                fn.write(
                    f'Modified: {mod_.strftime(TIME_FORMAT)},   '
                    f'created: {cre_.strftime(TIME_FORMAT)}\n')
                if not txt.startswith('#'):
                    ww = txt[:40].split()
                    fn.write(' '.join(
                        ('##', *ww[:-1], '\n')
                    ))
                fn.write(f'{txt}\n')

            def delete_notes_from_db():
                db_ut.delete_file_notes(self.file_id)
                db_ut.insert_note(self.file_id, link)
                ag.signals_.refresh_note_list.emit()

            note_file = Path(filepath.parent, f'{filepath.stem}.notes.md')
            old_content = read_note_file(note_file) if note_file.exists() else ''

            link = f"[{note_file.name}](file:///{note_file.as_posix().replace(' ', '%20')})"

            with open(note_file, "w") as fn:
                notes = db_ut.get_file_notes(self.file_id, desc=True)
                for txt, *_, md, cr in notes:
                    save_note()
                fn.write(old_content)
            delete_notes_from_db()

        filepath = Path(db_ut.get_file_path(self.file_id))
        menu = self.ui.textBrowser.createStandardContextMenu()
        acts = menu.actions()
        acts[1].setEnabled(bool(self.ui.textBrowser.anchorAt(pos)))
        menu.addSeparator()
        menu.addAction(f'Save "{filepath.name}" notes')
        act = menu.exec(self.ui.textBrowser.mapToGlobal(pos))
        if act:
            if act.text().startswith('Save'):
                save_notes_to_file()
            elif 'Link' in act.text():
                copy_link()

    def set_text(self, note: str):
        def set_note_title():
            # find first not empty line
            for pp in note.split('\n'):
                if pp:
                    txt = pp
                    break
            else:
                return
            self.ui.title.setText(txt[:40])

        self.text = note
        set_note_title()

    def set_browser_text(self):
        self.ui.textBrowser.setMarkdown(self.text)
        self.set_height_by_text()
        self.updateGeometry()

    def set_height_by_text(self):
        self.ui.textBrowser.document().setTextWidth(self.ui.textBrowser.width())
        size = self.ui.textBrowser.document().size().toSize()
        self.visible_height = size.height() + self.ui.item_header.height()

    def get_note_id(self) -> int:
        return self.id

    def set_file_id(self, file_id: int):
        self.file_id = file_id

    def get_file_id(self) -> int:
        return self.file_id

    def get_note_file_id(self) -> int:
        return self.note_file_id

    def sizeHint(self) -> QSize:
        return QSize(0, self.visible_height)

    @pyqtSlot()
    def toggle_collapse(self):
        self.collapsed = not self.collapsed
        self.collapse_item()

    def collapse_item(self):
        if self.collapsed:
            self.expanded_height = self.visible_height
            self.visible_height = self.ui.item_header.height()
            self.ui.textBrowser.hide()
        else:
            self.visible_height = self.expanded_height
            self.expanded_height = 0
            self.ui.textBrowser.show()
        self.set_collapse_icon(self.collapsed)

    @pyqtSlot()
    def check_collapse_button(self):
        if self.collapsed:
            return
        self.collapsed = True
        self.collapse_item()

    def set_collapse_icon(self, collapse: bool):
        self.ui.collapse.setIcon(
            tug.get_icon("right") if collapse
            else tug.get_icon("down")
        )

    @pyqtSlot()
    def edit_note(self):
        ag.signals_.start_edit_note.emit(self)

    @pyqtSlot()
    def remove_note(self):
        ag.signals_.delete_note.emit(self)

    @pyqtSlot(QUrl)
    def ref_clicked(self, href: QUrl):
        scheme = href.scheme()
        if scheme == 'fileid':
            ag.signals_.user_signal.emit(f'show file\\{href.fileName()}')
        elif scheme.startswith('http') or scheme == 'file':
            QDesktopServices.openUrl(href)

    def resizeEvent(self, a0: QResizeEvent) -> None:
        if not self.collapsed:
            self.set_browser_text()
        return super().resizeEvent(a0)
