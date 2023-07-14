from loguru import logger

from PyQt6.QtCore import Qt, QDateTime, QSize, pyqtSlot
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtWidgets import (QWidget, QTextEdit, QSizePolicy,
    QMessageBox, QTextBrowser, QStackedWidget, QPlainTextEdit,
    QVBoxLayout, QHBoxLayout, QToolButton, QFrame,
    QScrollArea, QAbstractScrollArea, QSizePolicy
)

from .ui_notes import Ui_FileNotes

from ..core import icons, app_globals as ag, db_ut
from ..core.compact_list import aBrowser
from .file_info import fileInfo
from .comment import Comment


class noteEditor(QTextEdit):
    def __init__(self, parent = None) -> None:
        super().__init__(parent)
        self.note_id = 0

    def set_note_id(self, note_id: int):
        self.note_id = note_id

    def get_note_id(self) -> int:
        return self.note_id

    def get_text(self):
        return self.toPlainText()


class tagBrowser(aBrowser):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

    def show_in_bpowser(self):
        style = ag.dyn_qss['text_browser'][0]
        self.browser.clear()

        txt = ''.join((style, self.html_selected()))

        self.browser.setText(txt)

    def html_selected(self):
        sel = self.selected_idx
        inn = ' '.join(f"<a class={'s' if i in sel else 't'} href=#{tag}>{tag}</a> "
             for i,tag in enumerate(self.tags))
        return inn


class authorBrowser(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.file_id = 0

        self.setup_ui()

        # list of authors changed outside, in ag.author_list
        ag.author_list.edit_finished.connect(self.refresh_data)

        self.br.change_selection.connect(self.update_selection)
        self.accept.clicked.connect(self.finish_edit_list)
        self.reject.clicked.connect(self.set_selected_text)

    def setup_ui(self):
        self.edit_authors = QPlainTextEdit()
        self.edit_authors.setObjectName('edit_authors')
        self.edit_authors.setMaximumSize(QSize(16777215, 42))
        si_policy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.edit_authors.setSizePolicy(si_policy)
        self.edit_authors.setToolTip(
            'Enter authors separated by commas, '
            'or select in the list below'
            ', use Ctrl+Click to select multiple items'
        )

        self.accept = QToolButton()
        self.accept.setObjectName('ok')
        self.accept.setIcon(icons.get_other_icon("ok"))
        self.accept.setToolTip('Accept editing')

        self.reject = QToolButton()
        self.reject.setObjectName('cancel')
        self.reject.setIcon(icons.get_other_icon("cancel2"))
        self.reject.setToolTip('Reject editing')

        v_layout = QVBoxLayout()
        v_layout.setContentsMargins(0, 0, 0, 0)
        v_layout.setSpacing(0)
        v_layout.addWidget(self.accept)
        v_layout.addWidget(self.reject)

        h_layout = QHBoxLayout()
        h_layout.setContentsMargins(0, 0, 0, 0)
        h_layout.setSpacing(0)
        h_layout.addWidget(self.edit_authors)
        h_layout.addLayout(v_layout)

        self.br = aBrowser(brackets=True)
        self.br.setObjectName('author_selector')

        authors = QFrame(self)
        authors.setObjectName('authors')
        f_layout = QVBoxLayout(self)
        f_layout.setContentsMargins(0, 0, 0, 0)

        m_layout = QVBoxLayout(authors)
        m_layout.setContentsMargins(0, 0, 0, 0)
        m_layout.setSpacing(0)
        m_layout.addLayout(h_layout)
        m_layout.addWidget(self.br)

        f_layout.addWidget(authors)

    def refresh_data(self):
        self.set_authors()
        self.set_selected_text()

    def set_authors(self):
        self.br.set_list(db_ut.get_authors())

    def set_file_id(self, id: int):
        self.file_id = id
        self.br.set_selection(
            (int(s[0]) for s in db_ut.get_file_author_id(id))
        )
        self.set_selected_text()

    @pyqtSlot()
    def set_selected_text(self):
        self.edit_authors.setPlainText(', '.join(
            (f'[{it}]' for it in self.br.get_selected())
        ))

    @pyqtSlot()
    def finish_edit_list(self):
        old = self.br.get_selected()
        new = self.get_edited_list()
        self.sel_list_changed(old, new)
        self.br.set_selection(
            (int(s[0]) for s in db_ut.get_file_author_id(self.file_id))
        )

    @pyqtSlot(list)
    def update_selection(self, items: list[str]):
        self.sel_list_changed(self.get_edited_list(), items)
        txt = (f'[{it}]' for it in items)
        self.edit_authors.setPlainText(', '.join(txt))

    def get_edited_list(self) -> list[str]:
        tt = self.edit_authors.toPlainText().strip()
        tt = tt.replace('[', '')
        pp = [t.strip() for t in tt.split('],') if t.strip()]
        if pp:
            if tt.endswith(']'):
                pp[-1] = pp[-1][:-1]
            else:
                qq = [t.strip() for t in pp[-1].split(',') if t.strip()]
                pp = [*pp[:-1], *qq]
        return pp

    def sel_list_changed(self, old: list[str], new: list[str]):
        # logger.info(f'{old=}, {new=}')
        self.remove_items(old, new)
        self.add_items(old, new)

    def remove_items(self, old: list[str], new: list[str]):
        diff = set(old) - set(new)
        # logger.info(f'{diff=}')
        for d in diff:
            if id := self.br.get_tag_id(d):
                db_ut.break_file_authors_link(self.file_id, id)

    def add_items(self, old: list[str], new: list[str]):
        inserted = False
        diff = set(new) - set(old)
        # logger.info(f'{diff=}')
        for d in diff:
            # logger.info(f'{self.file_id=}, {d=}')
            if db_ut.add_author(self.file_id, d):
                inserted = True
        if inserted:
            self.set_authors()
            ag.signals_.user_signal.emit("author_inserted")

def dir_type(dd: ag.DirData):
    """
    returns:
       '(L)' if folder is link to another folder,
       '(H)' if folder is hidden
       '(LH) if folder is link and is hidden
       empty string - otherwise
    """
    tt = f'{"L" if dd.is_link else ""}{"H" if dd.hidden else ""}'
    return f'({tt})' if tt else ''

class Locations(QTextBrowser):
    def __init__(self, parent = None) -> None:
        super().__init__(parent)
        self.file_id = 0
        self.branches = []
        self.dirs = []
        self.names = []

    def set_file_id(self, id: int):
        self.file_id = id
        self.get_locations()
        self.build_branch_data()
        self.show_branches()

    def get_locations(self):
        dir_ids = db_ut.get_file_dir_ids(self.file_id)
        self.get_file_dirs(dir_ids)
        self.branches.clear()
        self.curr = 0
        for dd in self.dirs:
            self.branches.append([(dd.id, dir_type(dd)), dd.parent_id])
            self.build_branches()

    def get_file_dirs(self, dir_ids):
        self.dirs.clear()
        for id in dir_ids:
            parents = db_ut.dir_parents(id[0])
            for pp in parents:
                self.dirs.append(ag.DirData(*pp))

    def build_branches(self):
        def add_dir_parent(qq: ag.DirData, tt: list) -> list:
            ss = [*tt[:-1]]
            tt[-1] = (qq.id, dir_type(qq))
            tt.append(qq.parent_id)
            return ss

        while 1:
            if self.curr >= len(self.branches):
                break
            tt = self.branches[self.curr]
            while 1:
                if tt[-1] == 0:
                    break
                parents = db_ut.dir_parents(tt[-1])
                first = True
                for pp in parents:
                    qq = ag.DirData(*pp)
                    if first:
                        ss = add_dir_parent(qq, tt)
                        first = False
                        continue
                    self.branches.append(
                        [*ss, (qq.id, dir_type(qq)), qq.parent_id]
                    )
            self.curr += 1

    def show_branches(self):
        txt = [
            '<table><tr><td><b>Path(Folder Tree branch)</b></td>',
        ]
        for a,b,c in self.names:
            # TODO create referencies to go to filder with popup menu
            txt.append(
                f'<tr><td>{a}</td>'
            )
        txt.append('</table>')
        self.setHtml(''.join(txt))

    def build_branch_data(self):
        self.names.clear()
        for bb in self.branches:
            self.names.append(self.branch_names(bb))

    def branch_names(self, bb: list) -> str:
        tt = bb[:-1]
        tt.reverse()
        is_link = 'Y' if bb[0][0] else ''
        hidden = 'Y' if bb[0][1] else ''
        ww = []
        for id in tt:
            name = db_ut.get_dir_name(id[0])
            ww.append(f'{name}{id[1]}')
        return ' > '.join(ww), is_link, hidden


class notesContainer(QScrollArea):
    def __init__(self, editor: noteEditor, parent: QWidget=None) -> None:
        super().__init__(parent)

        self.editor = editor
        self.set_ui()

        self.file_id = 0
        self.notes = {}

        ag.signals_.delete_note.connect(self.remove_item)

    def set_ui(self):
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setSizeAdjustPolicy(
            QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents
        )
        self.setWidgetResizable(True)
        self.setAlignment(
            Qt.AlignmentFlag.AlignLeading|
            Qt.AlignmentFlag.AlignLeft|
            Qt.AlignmentFlag.AlignTop
        )
        self.setObjectName("container")
        self.scrollWidget = QWidget()
        self.scrollWidget.setObjectName("scrollWidget")
        self.setWidget(self.scrollWidget)
        self.scroll_layout = QVBoxLayout(self.scrollWidget)
        self.scroll_layout.setObjectName('scroll_layout')

    def set_file_id(self, id: int):
        self.file_id = id
        self.set_notes_data()

    def set_notes_data(self):
        self.clear_layout()
        self.scroll_layout.addStretch(1)
        data = db_ut.get_file_notes(self.file_id)
        for row in data:
            note_id = row[2]
            note = Comment(*row[1:])
            note.set_text(row[0])
            self.notes[note_id] = note
            self.add_item(note)

    def clear_layout(self):
        while item := self.scroll_layout.takeAt(0):
            if item.widget():
                item.widget().deleteLater()

    def add_item(self, item: Comment):
        item.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.MinimumExpanding
        )
        self.scroll_layout.insertWidget(0, item)

    def get_note(self, id: int) -> Comment:
        return self.notes.get(id, None)

    def finish_editing(self, note_id: int):
        # logger.info(f'{note_id=}')
        if note_id:
            note = self.notes[note_id]
        else:
            note = Comment(file_id=self.file_id)
        self.update_note(note)
        self.add_item(note)

    def update_note(self, note: Comment):
        txt = self.editor.get_text()
        note_id = note.get_note_id()
        # logger.info(f'{note_id=}, {len(txt)=}')
        if note_id:
            self.scroll_layout.removeWidget(note)
            ts = db_ut.update_note(note.get_file_id(), note_id, txt)
        else:
            ts, id = db_ut.insert_note(self.file_id, txt)
            note.set_note_id(id)
            note.set_created_date(ts)
            self.notes[id] = note
        note.set_modified_date(ts)
        note.set_note_text(txt)

        self.update_date_in_file_list(ts)

    def update_date_in_file_list(self, ts: int):
        if ts > 0:
            a = QDateTime()
            a.setSecsSinceEpoch(ts)
            ag.file_list.model().update_field_by_name(
                a, "Commented", ag.file_list.currentIndex()
            )

    @pyqtSlot(int)
    def remove_item(self, note_id: int):
        if self.confirm_note_deletion():
            note = self.notes.pop(note_id, None)
            self.scroll_layout.removeWidget(note)
            db_ut.delete_note(note.get_file_id(), note_id)

    def confirm_note_deletion(self):
        dlg = QMessageBox(ag.app)
        dlg.setWindowTitle('delete file note')
        dlg.setText(f'confirm deletion of note')
        dlg.setStandardButtons(QMessageBox.StandardButton.Ok |
            QMessageBox.StandardButton.Cancel)
        dlg.setIcon(QMessageBox.Icon.Question)
        return dlg.exec() == QMessageBox.StandardButton.Ok

    def collapse_all(self):
        for note in self.notes.values():
            note: Comment
            note.check_collapse_button()


class notesBrowser(QWidget, Ui_FileNotes):
    def __init__(self, parent = None) -> None:
        super().__init__(parent)
        self.file_id = 0
        self.id = 0
        self.maximized = False
        self.s_height = 0

        self.setupUi(self)

        self.page_selectors = [
            self.l_tags, self.l_authors,
            self.l_locations, self.l_file_info,
            self.l_comments, self.l_editor,
        ]
        self.set_stack_pages()
        self.l_editor.hide()

        ag.signals_.start_edit_note.connect(self.start_edit)

        self.expand.setIcon(icons.get_other_icon("up"))
        self.expand.clicked.connect(self.up_down)

        self.plus.setIcon(icons.get_other_icon("plus"))
        self.plus.clicked.connect(self.new_comment)

        self.collapse_all.setIcon(icons.get_other_icon("collapse_all"))
        self.collapse_all.clicked.connect(self.notes.collapse_all)

        self.save.setIcon(icons.get_other_icon("ok"))
        self.save.clicked.connect(self.note_changed)

        self.cancel.setIcon(icons.get_other_icon("cancel2"))
        self.cancel.clicked.connect(self.cancel_note_editing)

        self.edit_btns.hide()
        self.note_btns.hide()
        self.tagEdit.editingFinished.connect(self.finish_edit_tag)

        self.cur_page = 0
        self.l_comments_press(None)

        self.l_tags.mousePressEvent = self.l_tags_press
        self.l_authors.mousePressEvent = self.l_authors_press
        self.l_locations.mousePressEvent = self.l_locations_press
        self.l_file_info.mousePressEvent = self.l_file_info_press
        self.l_comments.mousePressEvent = self.l_comments_press
        self.l_editor.mousePressEvent = self.l_editor_press

    def set_stack_pages(self):
        self.stackedWidget = QStackedWidget(self)
        self.stackedWidget.setObjectName("stackedWidget")

        # add tag selector page (0)
        self.tag_selector = tagBrowser(self)
        self.stackedWidget.addWidget(self.tag_selector)
        self.tag_selector.setObjectName('tag_selector')
        self.tag_selector.change_selection.connect(self.update_tags)
        ag.tag_list.edit_finished.connect(self.update_tag_list)

        # add author selector page (1)
        self.author_selector = authorBrowser()
        self.stackedWidget.addWidget(self.author_selector)
        self.author_selector.setObjectName('author_selector')

        # add file locations page (2)
        self.locator = Locations(self)
        self.stackedWidget.addWidget(self.locator)
        self.locator.setObjectName('locator')

        # add file info page (3)
        self.file_info = fileInfo(self)
        self.file_info.setObjectName('file_info')
        self.stackedWidget.addWidget(self.file_info)

        self.editor = noteEditor()
        self.editor.setObjectName('note_editor')

        self.notes = notesContainer(self.editor, self)
        self.notes.setObjectName('notes_container')

        # add comments page (4)
        self.stackedWidget.addWidget(self.notes)
        # add comment editor page (5)
        self.stackedWidget.addWidget(self.editor)

        ss = ag.dyn_qss['passive_selector'][0]
        for lbl in self.page_selectors:
            lbl.setStyleSheet(ss)

        self.main_layout.addWidget(self.stackedWidget)
        self.setStyleSheet(' '.join(ag.dyn_qss['noteFrames']))

    def l_tags_press(self, e: QMouseEvent):
        # tag selector page
        self.switch_page(0)
        self.note_btns.hide()

    def l_authors_press(self, e: QMouseEvent):
        # author selector page
        self.switch_page(1)
        self.note_btns.hide()

    def l_locations_press(self, e: QMouseEvent):
        # file locations page
        self.switch_page(2)
        self.note_btns.hide()

    def l_file_info_press(self, e: QMouseEvent):
        # file info page
        self.switch_page(3)
        self.note_btns.hide()

    def l_comments_press(self, e: QMouseEvent):
        # comments page
        self.switch_page(4)
        self.note_btns.show()

    def l_editor_press(self, e: QMouseEvent):
        # editor page
        self.switch_page(5)
        self.note_btns.hide()
        self.edit_btns.show()

    def switch_page(self, page_no: int):
        self.page_selectors[self.cur_page].setStyleSheet(
            ag.dyn_qss['passive_selector'][0]
        )
        self.page_selectors[page_no].setStyleSheet(
            ag.dyn_qss['active_selector'][0]
        )
        if self.cur_page == 5 and page_no != 5:
            self.edit_btns.hide()
        self.cur_page = page_no
        self.stackedWidget.setCurrentIndex(page_no)

    def up_down(self):
        if self.maximized:
            self.expand.setIcon(icons.get_other_icon("up"))
            ag.app.ui.noteHolder.setMinimumHeight(self.s_height)
            ag.app.ui.noteHolder.setMaximumHeight(self.s_height)
            ag.file_list.show()
        else:
            self.s_height = self.height()
            self.expand.setIcon(icons.get_other_icon("down"))
            hh = ag.file_list.height() + self.s_height
            ag.app.ui.noteHolder.setMinimumHeight(hh)
            ag.app.ui.noteHolder.setMaximumHeight(hh)
            ag.file_list.hide()
        self.maximized = not self.maximized

    def cancel_note_editing(self):
        self.l_editor.hide()
        self.l_comments_press(None)

    def note_changed(self):
        note_id = self.editor.get_note_id()
        logger.info(f'{note_id=}')
        self.notes.finish_editing(note_id)
        self.l_editor.hide()
        self.l_comments_press(None)

    def set_data(self):
        self.tag_selector.set_list(db_ut.get_tags())
        self.author_selector.set_authors()

    @pyqtSlot()
    def update_tag_list(self):
        self.tag_selector.set_list(db_ut.get_tags())

    @pyqtSlot()
    def finish_edit_tag(self):
        old = self.tag_selector.get_selected()
        new = self.new_tag_list()
        self.tag_list_changed(old, new)

    def tag_list_changed(self, old: list[str], new: list[str]):
        self.remove_tags(old, new)
        if self.add_tags(old, new):
            self.update_tag_list()
            ag.signals_.user_signal.emit("tag_inserted")

    def new_tag_list(self):
        """
        tag can't contain blanks and can't be empty string
        """
        tmp = self.tagEdit.text().replace(' ','')
        return [t for t in tmp.split(',') if t]

    def remove_tags(self, old: list[str], new: list[str]):
        diff = set(old) - set(new)
        for d in diff:
            id = self.tag_selector.get_tag_id(d)
            db_ut.delete_tag_file(id, self.file_id)

    def add_tags(self, old, new) -> bool:
        inserted = False
        diff = set(new) - set(old)
        for d in diff:
            if not (id := self.tag_selector.get_tag_id(d)):
                id = db_ut.insert_tag(d)
                inserted = True
            db_ut.insert_tag_file(id, self.file_id)
        return inserted

    def new_comment(self):
        self.show_editor(0, '')

    def start_edit(self, note_id: int):
        note = self.notes.get_note(note_id)
        txt = db_ut.get_note(note.get_file_id(), note_id)
        self.show_editor(note_id, txt)

    def show_editor(self, note_id: int, txt: str):
        self.editor.setText(txt)
        self.editor.set_note_id(note_id)

        self.note_btns.hide()
        self.edit_btns.show()
        self.l_editor.show()
        self.switch_page(5)
        self.editor.setFocus()

    def set_file_id(self, id: int):
        self.file_id = id
        self.tag_selector.set_selection(
            (int(s[0]) for s in db_ut.get_file_tagid(self.file_id))
        )
        self.tagEdit.setText(', '.join(
            self.tag_selector.get_selected()
            )
        )
        self.file_info.set_file_id(id)
        self.author_selector.set_file_id(id)
        self.locator.set_file_id(id)
        self.notes.set_file_id(id)

    @pyqtSlot(list)
    def update_tags(self, tags: list[str]):
        self.tag_list_changed(self.new_tag_list(), tags)
        self.tagEdit.setText(', '.join(tags))
