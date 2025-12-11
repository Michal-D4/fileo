# from loguru import logger
import markdown
from datetime import datetime
from pathlib import Path
import re
from enum import Enum, unique

from PyQt6.QtCore  import Qt, QUrl, pyqtSlot, QSize, QPoint, QRegularExpression
from PyQt6.QtGui import QDesktopServices, QResizeEvent, QAction, QKeySequence, QTextDocument, QTextCursor, QFocusEvent
from PyQt6.QtWidgets import QWidget, QApplication, QMenu

from ..core import app_globals as ag, db_ut
from .ui_file_note import Ui_fileNote
from .. import tug

TIME_FORMAT = "%Y-%m-%d %H:%M"

@unique
class Direction(Enum):
    Next = 1
    Prev = 2


class fileNote(QWidget):
    srch_pattern = ''
    srch_flag: QTextDocument.FindFlag = QTextDocument.FindFlag(0)
    current_note: 'fileNote' = None

    def __init__(self,
                 file_id: int = 0,
                 note_id: int=0,
                 modified: int=0,
                 created: int=0,
                 parent: QWidget=None) -> None:
        super().__init__(parent)

        self.file_id = int(file_id)
        self.note_id = int(note_id)

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

        self.ui.collapse.toggled.connect(self.toggle_collapse)
        self.ui.edit.clicked.connect(self.edit_note)
        self.ui.remove.clicked.connect(self.remove_note)
        self.ui.textBrowser.anchorClicked.connect(self.ref_clicked)
        self.ui.textBrowser.focusInEvent = self.browser_get_focus

        self.set_collapse_icon()

        self.ui.textBrowser.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.ui.textBrowser.customContextMenuRequested.connect(self.context_menu)
        self.resizeEvent = self.note_resize

    @classmethod
    def set_current_note(cls, note: 'fileNote'):
        cls.current_note = note

    def browser_get_focus(self, a0: QFocusEvent):
        if a0.reason() is Qt.FocusReason.MouseFocusReason:
            self.set_current_note(self)
            pos = self.ui.textBrowser.cursor().pos()
            self.ui.textBrowser.cursorForPosition(self.ui.textBrowser.mapFromGlobal(pos))
        return super().focusInEvent(a0)

    @classmethod
    def set_search_options(cls):
        if ag.mode is ag.appMode.FOUND_IN_NOTES:
            srch_obj = ag.popups.get('srchInNotes', None)
            srch_opt: dict = srch_obj.srch_params()
            txt = srch_opt.get('txt', '')

            if srch_opt.get('rex', 0):
                cls.srch_pattern = QRegularExpression(txt)
            else:
                cls.srch_pattern = txt

            cls.srch_flag = QTextDocument.FindFlag(0)
            if srch_opt.get('whole_word', 0):
                cls.srch_flag = QTextDocument.FindFlag.FindWholeWords
            if srch_opt.get('case', 0):
                cls.srch_flag = cls.srch_flag | QTextDocument.FindFlag.FindCaseSensitively

    def add_buttons(self):
        ag.note_buttons.append((self.ui.edit, "toEdit"))
        ag.note_buttons.append((self.ui.remove, "cancel2"))
        ag.note_buttons.append((self.ui.collapse, "down3", "right3"))

    @pyqtSlot(QPoint)
    def context_menu(self, pos: QPoint):
        def copy_link():
            QApplication.clipboard().setText(self.ui.textBrowser.anchorAt(pos))

        def copy_html():
            QApplication.clipboard().setText(self.ui.textBrowser.toHtml())

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
                note_text = f'{link}  `Created: {datetime.now().strftime(TIME_FORMAT)}`'
                db_ut.insert_note(self.file_id, note_text)
                ag.signals.refresh_note_list.emit()

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
        menu = QMenu(self)
        menu.setStyleSheet(tug.get_dyn_qss('note_menu'))
        if self.ui.textBrowser.textCursor().selectedText():
            act_copy = QAction("Copy\tCtrl+C")
            act_copy.setShortcut(QKeySequence.StandardKey.Copy)
            menu.addAction(act_copy)
            menu.addSeparator()
        anch = self.ui.textBrowser.anchorAt(pos)
        if anch:
            menu.addAction("Copy Link Location")
            menu.addSeparator()
        menu.addAction("Select All\tCtrl+A")
        menu.addSeparator()
        if anch.startswith('fileid:'):
            menu.addAction("Open file")
            menu.addSeparator()
        menu.addAction('Copy HTML')
        menu.addAction(f'Save "{filepath.name}" notes')
        act = menu.exec(self.ui.textBrowser.mapToGlobal(pos))
        if act:
            if act.text().startswith('Save'):
                save_notes_to_file()
            elif 'Link' in act.text():
                copy_link()
            elif 'All' in  act.text():
                self.ui.textBrowser.selectAll()
            elif act.text().startswith('Copy\t'):
                self.ui.textBrowser.copy()
            elif act.text() == 'Copy HTML':
                copy_html()
            elif act.text() == 'Open file':
                file_id = self.ui.textBrowser.anchorAt(pos)[8:]
                ag.signals.user_signal.emit(f'Open file by path\\{db_ut.get_file_path(file_id)}')

    def set_text(self, note: str, plain: bool):
        def set_note_title():
            # find first not empty line
            for pp in note.splitlines():
                if pp:
                    txt = pp
                    break
            else:
                return
            wth = int(tug.qss_params.get('$note_title_width', 40))
            self.ui.note_title.setText(txt[:wth])

        def except_image(txt) -> str:
            parts = []
            pos = 0
            while 1:
                pp = txt.find('<img src', pos)
                if pp == -1:
                    parts.append(txt[pos:].replace('<', '&lt;').replace('>', '&gt;'))
                    break
                parts.append(txt[pos:pp].replace('<', '&lt;').replace('>', '&gt;'))
                pos = txt.find('/>', pp)
                pos = pos+2 if pos > pp else len(txt)
                parts.append(txt[pp:pos])
            return ''.join(parts)

        def replace_lt_gt() -> str:
            parts = []
            repl = True
            for pp in note.split('`'):
                if repl:
                    if pp.rfind('</') == -1:
                        pp = except_image(pp)
                parts.append(pp)
                repl = not repl
            return f'\n{'`'.join(parts) if len(parts) > 1 else parts[0]}'

        if plain:
            self.text = note
            self.ui.textBrowser.setPlainText(note)
        else:
            self.text = replace_lt_gt()
            self.set_browser_text()

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
        self.ui.textBrowser.setHtml(' '.join((tug.get_dyn_qss("link_style"), txt)))

    def find_pattern(self, direction: Direction = Direction.Next) -> int:
        flag = self.srch_flag
        if direction is Direction.Prev:
            flag |= QTextDocument.FindFlag.FindBackward

        curs = self.ui.textBrowser.textCursor()
        doc = self.ui.textBrowser.document()

        curs1: QTextCursor = doc.find(self.srch_pattern, curs, flag)
        self.ui.textBrowser.setTextCursor(curs if curs1.position() == -1 else curs1)
        return curs1.position()

    def cursor_location(self) -> QPoint:
        return self.ui.textBrowser.cursorRect().topLeft()

    def set_cursor_position(self, pos: QTextCursor.MoveOperation=QTextCursor.MoveOperation.End):
        cursor = self.ui.textBrowser.textCursor()
        cursor.movePosition(pos)
        self.ui.textBrowser.setTextCursor(cursor)

    def set_height_by_text(self):
        if self.ui.collapse.isChecked():
            return
        self.ui.textBrowser.document().setTextWidth(ag.file_data.width())
        size = self.ui.textBrowser.document().size().toSize()
        self.visible_height = size.height() + self.ui.note_header.height()

    def get_note_id(self) -> int:
        return self.note_id

    def get_file_id(self) -> int:
        return self.file_id

    def sizeHint(self) -> QSize:
        return QSize(0, self.visible_height)

    @pyqtSlot(bool)
    def toggle_collapse(self, state: bool):
        self.hide_note(state)    # True ==> collapsed

    def hide_note(self, state: bool):
        if state:
            self.expanded_height = self.visible_height
            self.visible_height = self.ui.note_header.height()
        else:
            self.visible_height = self.expanded_height
            self.expanded_height = 0
        self.ui.textBrowser.setVisible(not state)
        self.set_collapse_icon()

    @pyqtSlot()
    def ensure_collapsed(self):
        if self.ui.collapse.isChecked():
            return
        self.ui.collapse.setChecked(True)
        self.hide_note(self.ui.collapse.isChecked())

    def set_collapse_icon(self):
        self.ui.collapse.setIcon(
            tug.get_icon("right3") if self.ui.collapse.isChecked() else tug.get_icon("down3")
        )

    @pyqtSlot()
    def edit_note(self):
        ag.signals.start_edit_note.emit(self)

    @pyqtSlot()
    def remove_note(self):
        ag.signals.delete_note.emit(self)

    @pyqtSlot(QUrl)
    def ref_clicked(self, href: QUrl):
        scheme = href.scheme()
        if scheme == 'fileid':
            ag.signals.user_signal.emit(f'show file\\{href.fileName()}')
        elif scheme.startswith('http') or scheme == 'file':
            QDesktopServices.openUrl(href)

    def note_resize(self, e: QResizeEvent):
        self.set_height_by_text()