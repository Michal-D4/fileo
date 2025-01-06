# from loguru import logger
import markdown
from datetime import datetime
from pathlib import Path
import re

from PyQt6.QtCore  import Qt, QUrl, pyqtSlot, QSize, QPoint
from PyQt6.QtGui import QDesktopServices, QResizeEvent
from PyQt6.QtWidgets import QWidget, QApplication

from ..core import app_globals as ag, db_ut
from .ui_file_note import Ui_fileNote
from .. import tug

TIME_FORMAT = "%Y-%m-%d %H:%M"


class fileNote(QWidget):

    def __init__(self,
                 file_id: int = 0,
                 note_id: int=0,
                 modified: int=0,
                 created: int=0,
                 parent: QWidget=None) -> None:
        super().__init__(parent)

        self.file_id = file_id
        self.id = note_id

        self.modified = datetime.fromtimestamp(modified)
        self.created = datetime.fromtimestamp(created)
        self.text = ''

        self.visible_height = 0
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

        self.set_collapse_icon()
        if self.id:
            ag.note_buttons.append((self.ui.edit, "toEdit"))
            ag.note_buttons.append((self.ui.remove, "cancel2"))
            ag.note_buttons.append((self.ui.collapse, "down3", "right3"))

        self.ui.textBrowser.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.ui.textBrowser.customContextMenuRequested.connect(self.context_menu)
        self.resizeEvent = self.note_resize

    @pyqtSlot(QPoint)
    def context_menu(self, pos: QPoint):
        def copy_link():
            QApplication.clipboard().setText(self.ui.textBrowser.anchorAt(pos))

        def read_note_file(pp: Path):
            with open(pp) as ff:
                return ff.read()

        def save_notes_to_file():
            def prepare_note_text() -> str:
                def create_title() -> str:
                    uu = ttt[0][:40].split()
                    uu = uu[:-1] if len(ttt[0]) > 40 else uu
                    return ' '.join(('##', *uu, '\n'))

                modi = datetime.fromtimestamp(md)
                crea = datetime.fromtimestamp(cr)
                vvv = (
                    f'`Modified: {modi.strftime(TIME_FORMAT)};   '
                    f'Created: {crea.strftime(TIME_FORMAT)}`\n'
                )
                ttt = txt.splitlines()
                if ttt[0].startswith('#'):
                    return '\n'.join((ttt[0], vvv, *ttt[1:]))
                return '\n'.join((create_title(), vvv, *ttt))

            def delete_notes_from_db():
                db_ut.delete_file_notes(self.file_id)
                note_text = f'{link}`     Created: {datetime.now().strftime(TIME_FORMAT)}`'
                db_ut.insert_note(self.file_id, note_text)
                ag.signals_.refresh_note_list.emit()

            note_file = Path(filepath.parent, f'{filepath.stem}.notes.md')
            old_content = read_note_file(note_file) if note_file.exists() else ''

            link = f"[{note_file.name}](file:///{str(note_file).replace(' ', '%20')})"

            with open(note_file, "w") as fn:
                fn.write(
                    f'{note_file.name},    `Created: '
                    f'{datetime.now().strftime(TIME_FORMAT)}`\n***\n'
                )
                notes = db_ut.get_file_notes(self.file_id, desc=True)
                for txt, *_, md, cr in notes:
                    # _ = fileid, noteid
                    if link in txt:
                        continue
                    fn.write(prepare_note_text())
                    fn.write('\n***\n')

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
            for pp in note.splitlines():
                if pp:
                    txt = pp
                    break
            else:
                return
            wth = tug.config['note_title_width']
            self.ui.note_title.setText(txt[:wth])

        prep = f'\n{note}'
        prep = prep.replace('<<', '&#60')
        prep = prep.replace('>>', '&#62')
        self.text = prep
        set_note_title()

    def set_browser_text(self):
        def code_block_ally(txt: str) -> str:
            t = re.search(r'\n *```', txt)
            if not t:
                return txt
            j = t.span()[1]
            i = j - 3
            j = txt.find('\n', j) + 1
            t = re.search(r'\n *```', txt[j:])
            if not t:
                return txt
            q = t.span()[1] + j
            k = q - 3
            return ''.join((txt[:i], "<pre><code>", txt[j:k], "</code></pre>", code_block_ally(txt[q:])))

        if not self.text:
            return

        txt = code_block_ally(self.text)
        txt = markdown.markdown(txt[1:])
        self.ui.textBrowser.setHtml(' '.join(
            (tug.get_dyn_qss("link_style"), txt)
        ))

    def set_height_by_text(self):
        if self.ui.collapse.isChecked():
            return
        self.ui.textBrowser.document().setTextWidth(self.ui.textBrowser.width())
        size = self.ui.textBrowser.document().size().toSize()
        self.visible_height = size.height() + self.ui.note_header.height()

    def get_note_id(self) -> int:
        return self.id

    def get_file_id(self) -> int:
        return self.file_id

    def sizeHint(self) -> QSize:
        return QSize(0, self.visible_height)

    @pyqtSlot()
    def toggle_collapse(self):
        self.view_note()

    def view_note(self):
        if self.ui.collapse.isChecked():
            self.expanded_height = self.visible_height
            self.visible_height = self.ui.note_header.height()
            self.ui.textBrowser.hide()
        else:
            self.visible_height = self.expanded_height
            self.expanded_height = 0
            self.set_browser_text()
            self.ui.textBrowser.show()
        self.set_collapse_icon()

    @pyqtSlot()
    def ensure_collapsed(self):
        if self.ui.collapse.isChecked():
            return
        self.ui.collapse.setChecked(True)
        self.view_note()

    def set_collapse_icon(self):
        self.ui.collapse.setIcon(
            tug.get_icon("right3") if self.ui.collapse.isChecked()
            else tug.get_icon("down3")
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

    def note_resize(self, e: QResizeEvent):
        self.set_height_by_text()