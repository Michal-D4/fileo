from loguru import logger

from PyQt6.QtCore import Qt, QUrl, QDateTime, QPoint
from PyQt6.QtGui import QGuiApplication, QResizeEvent, QMouseEvent
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
    QFrame, QSpacerItem, QSizePolicy, QToolButton, QTextEdit,
    QMessageBox, QTextBrowser, QStackedWidget, QLineEdit
)

from datetime import datetime

from .ui_notes import Ui_FileNotes

from core import icons, app_globals as ag, db_ut
from core.compact_list import aBrowser
from widgets.file_info import fileInfo

time_format = "%Y-%m-%d %H:%M"

class noteEditor(QTextEdit):
    def __init__(self, parent = None) -> None:
        super().__init__(parent)
        self.id = 0

    def set_note_id(self, id: int):
        self.id = id

    def get_note_id(self) -> int:
        return self.id


class tagBrowser(aBrowser):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

    def show_in_bpowser(self):
        style = ag.dyn_qss['text_browser'][0]
        self.browser.clear()

        txt = ''.join((style, self.html_selected()))

        self.browser.setText(txt)

    def get_tag_id(self, tag: str) -> bool:
        try:
            return self.tag_ids[self.tags.index(tag)]
        except ValueError:
            return 0

    def html_selected(self):
        sel = self.selected_idx
        inn = ' '.join(f"<a class={'s' if i in sel else 't'} href=#{tag}>{tag}</a> "
             for i,tag in enumerate(self.tags))
        return inn


class authorBrowser(QWidget):
    def __init__(self, parent=None) -> None:

        self.br = aBrowser()
        self.br.show_in_bpowser = self.show_in_bpowser

    def show_in_bpowser(self):
        style = ag.dyn_qss['text_browser'][0]
        self.br.browser.clear()

        txt = ''.join((style, self.html_selected()))

        self.br.browser.setText(txt)

    def html_selected(self):
        sel = self.selected_idx
        inn = ' '.join(f"<a class={'s' if i in sel else 't'} href=#{tag}>[{tag}]</a> "
             for i,tag in enumerate(self.tags))
        return inn

#region file_info
def populate_file_authors(self):
    """
    from authors table
    """
    fa_curs = db_ut.get_file_authors(self.id)
    file_authors = []
    for author in fa_curs:
        file_authors.append(author[0])
    self.file_authors.setPlainText(', '.join(file_authors))

def populate_combo(self):
    # move to
    a_curs = db_ut.get_authors()
    for author, udat in a_curs:
        self.combo.addItem(author, udat)

def custom_menu(self, pos):
    from PyQt6.QtWidgets import QMenu
    menu = QMenu(self)
    menu.addAction("Delete selected")
    menu.addAction("Copy selected")
    menu.addSeparator()
    menu.addAction("Select all")
    action = menu.exec(self.file_authors.mapToGlobal(pos))
    if action:
        {'Delete selected': self.delete_link,
            'Copy selected': self.copy_selected,
            'Select all': self.select_all
        }[action.text()]()

def copy_selected(self):
    from PyQt6.QtWidgets import QApplication
    curs = self.file_authors.textCursor()
    QApplication.clipboard().setText(curs.selectedText())

def select_all(self):
    self.file_authors.selectAll()

def delete_link(self):
    curs = self.file_authors.textCursor()
    if curs.hasSelection():
        sel_txt = curs.selectedText()
        for txt in sel_txt.split(', '):
            i = self.combo.findText(txt, Qt.MatchFlag.MatchExactly)
            if i == -1:
                continue
            id = self.combo.itemData(i, Qt.ItemDataRole.UserRole)
            db_ut.break_file_authors_link(self.id, id)
        self.populate_file_authors()

def select_on_click(self, e: QMouseEvent):
    pos = e.pos()
    sel = self.file_authors.textCursor().selectedText()
    if sel and e.button() == Qt.MouseButton.RightButton:
        return
    txt_curs_at_click = self.file_authors.cursorForPosition(pos)
    self.file_authors.setTextCursor(txt_curs_at_click)
    text_pos = self.file_authors.textCursor().position()

    self.select_author_under_pos(text_pos)

def select_author_under_pos(self, pos: int):
    from PyQt6.QtGui import QTextCursor
    txt = self.file_authors.toPlainText()
    left = left_comma(pos, txt)
    right = right_comma(pos, txt)

    curs = self.file_authors.textCursor()
    curs.movePosition(
        QTextCursor.MoveOperation.PreviousCharacter,
        QTextCursor.MoveMode.MoveAnchor, pos-left
    )
    curs.movePosition(
        QTextCursor.MoveOperation.NextCharacter,
        QTextCursor.MoveMode.KeepAnchor, right-left
    )

    self.file_authors.setTextCursor(curs)
def new_choice(self, idx: int):
    """
    add link author-file for the current file
    """
    author = self.combo.currentText()
    if not self.fill_file_authors(author):       # author already exists
        return

    # create new author
    id = db_ut.add_author(self.id, author)
    if id:
        self.combo.addItem(author, id)
        ag.signals_.user_action_signal.emit("author inserted")

def fill_file_authors(self, author: str) -> bool:
    txt = self.file_authors.toPlainText()
    authors = txt.split(', ') if txt else []
    if author in authors:
        return False
    authors.append(author)
    authors.sort()
    self.file_authors.setPlainText(', '.join(authors))
    return True

def left_comma(pos: int, txt: str) -> int:
    comma_pos = txt[:pos].rfind(',')
    return 0 if comma_pos == -1 else comma_pos+2

def right_comma(pos: int, txt: str) -> int:
    comma_pos = txt[pos:].find(',')
    return len(txt) if comma_pos == -1 else pos + comma_pos
#endregion

class notesBrowser(QWidget, Ui_FileNotes):
    def __init__(self, parent = None) -> None:
        super().__init__(parent)
        self.tags = []
        self.tag_id = []
        self.selected = []
        self.file_id = 0
        self.id = 0

        self.setupUi(self)

        self.edit_tag = QLineEdit(self)
        self.edit_tag.setInputMask('n'*20)
        self.edit_tag.setGeometry(0, 0, 100, 24)
        self.edit_tag.editingFinished.connect(self.new_tag_created)
        self.edit_tag.hide()

        self.page_selectors = [
            self.l_tags, self.l_authors,
            self.l_locations, self.l_file_info,
            self.l_comments
        ]
        self.set_stack_pages()

        self.plus.setIcon(icons.get_other_icon("plus"))
        self.plus.clicked.connect(self.new_comment)

        self.save.setIcon(icons.get_other_icon("ok"))
        self.save.clicked.connect(self.note_changed)

        self.cancel.setIcon(icons.get_other_icon("cancel2"))
        self.cancel.clicked.connect(self.cancel_note_editing)

        self.edit_btns.hide()
        self.plus.hide()

        self.add.setIcon(icons.get_other_icon("plus"))
        self.add.clicked.connect(self.create_new_tag)

        self.browser.anchorClicked.connect(self.ref_clicked)

        self.cur_page = 0
        self.l_comments_press(None)

        self.l_tags.mousePressEvent = self.l_tags_press
        self.l_authors.mousePressEvent = self.l_authors_press
        self.l_locations.mousePressEvent = self.l_locations_press
        self.l_file_info.mousePressEvent = self.l_file_info_press
        self.l_comments.mousePressEvent = self.l_comments_press

    def set_stack_pages(self):
        self.stackedWidget = QStackedWidget(self)
        self.stackedWidget.setObjectName("stackedWidget")

        # add tag selector page (0)
        self.tag_selector = tagBrowser(self)
        self.stackedWidget.addWidget(self.tag_selector)
        self.tag_selector.setObjectName('tag_selector')
        self.tag_selector.change_selection.connect(self.update_tags)

        # add author selector page (1)
        self.author_selector = tagBrowser()
        self.stackedWidget.addWidget(self.author_selector)
        self.author_selector.setObjectName('author_selector')
        # self.author_selector.set_list()
        # self.author_selector.set_selection()

        # add file locations page (2)
        self.locator = QTextBrowser(self)
        self.stackedWidget.addWidget(self.locator)
        self.locator.setObjectName('locator')

        # add file info page (3)
        self.file_info = fileInfo(self)
        self.stackedWidget.addWidget(self.file_info)

        # add comments page (4)
        self.browser = QTextBrowser(self)
        self.stackedWidget.addWidget(self.browser)
        self.browser.setOpenLinks(False)
        self.browser.setObjectName('notes_browser')

        # add comment editor page (5)
        self.editor = noteEditor()
        self.stackedWidget.addWidget(self.editor)
        self.editor.setObjectName('note_editor')

        ss = ag.dyn_qss['passive_selector'][0]
        for lbl in self.page_selectors:
            lbl.setStyleSheet(ss)

        self.verticalLayout.addWidget(self.stackedWidget)
        self.setStyleSheet(' '.join(ag.dyn_qss['noteFrames']))

    def l_tags_press(self, e: QMouseEvent):
        self.switch_page(0)

    def l_authors_press(self, e: QMouseEvent):
        self.switch_page(1)

    def l_locations_press(self, e: QMouseEvent):
        self.switch_page(2)

    def l_file_info_press(self, e: QMouseEvent):
        self.switch_page(3)

    def l_comments_press(self, e: QMouseEvent):
        self.switch_page(4)
        self.plus.show()

    def switch_page(self, page_no: int):
        logger.info(f'{page_no=}, {self.cur_page=}')
        if page_no < 5 and self.cur_page < 5:
            self.page_selectors[self.cur_page].setStyleSheet(
                ag.dyn_qss['passive_selector'][0]
            )
            self.page_selectors[page_no].setStyleSheet(
                ag.dyn_qss['active_selector'][0]
            )
        if self.cur_page == 5 and page_no != 5:
            self.edit_btns.hide()
        if self.cur_page == 4 and page_no != 4:
            self.plus.hide()
        self.cur_page = page_no
        self.stackedWidget.setCurrentIndex(page_no)

    def cancel_note_editing(self):
        self.l_comments_press(None)

    def note_changed(self):
        id = self.editor.get_note_id()
        txt = self.editor.toPlainText()
        if id:
            ts = db_ut.update_note(self.file_id, id, txt)
        else:
            ts = db_ut.insert_note(self.file_id, txt)

        if ts > 0:
            a = QDateTime()
            a.setSecsSinceEpoch(ts)
            ag.file_list.model().update_field_by_name(
                a, "Commented", ag.file_list.currentIndex()
            )
            self.set_notes_data(db_ut.get_file_notes(self.file_id))
        self.l_comments_press(None)

    def set_tag_list(self, tags: list):
        self.tag_selector.set_list(tags)

    def create_new_tag(self) -> str:
        logger.info(f'{self.add.pos()=}')
        self.edit_tag.move(self.add.pos()+QPoint(-100, 22))
        self.edit_tag.setText('<<< KU_KU >>>')
        self.edit_tag.show()
        logger.info(f'{self.edit_tag.isHidden()=}')
        logger.info(f'{self.edit_tag.geometry()=}')

    def new_tag_created(self):
        tag = self.edit_tag.text()
        logger.info(f'{tag=}, id: {self.tag_selector.get_tag_id(tag)}')
        self.edit_tag.hide()
        if self.tag_selector.get_tag_id(tag):
            if tag in self.tagEdit.text():
                return
        old = self.tag_selector.get_selected()
        new = [*old, tag]
        new.sort()
        self.tag_list_changed()
        self.tagEdit.setText(', '.join(new))
        # self.tag_list_changed(old)

    # def tag_list_changed(self, old: list[str]):
    def tag_list_changed(self):
        new = self.tag_selector.get_selected()
        old = [
            t for t in self.tagEdit.text().split(', ') if t
        ]

        logger.info(f'{old=}, {new=}')

        # self.remove_tags(old, new)
        if self.add_tags(old, new):
            ag.signals_.user_action_signal.emit("tag_inserted")

    def add_tags(self, old, new) -> bool:
        ret = False
        diff = set(new) - set(old)
        for d in diff:   # only new in diff
            if not (id := self.tag_selector.get_tag_id(d)):
                id = db_ut.insert_tag(d)
                ret = True
            logger.info(f'{id=}, {self.file_id=}')
            db_ut.insert_tag_file(id, self.file_id)
        return ret

    def section_title(self, id: int, mod: str, cre: str) -> str:
        btn1 = f'<span class="fa"><a class=t href=x,lnk{id}>&#xf00d;</a></span>'
        btn2 = f'<span class="fa"><a class=t href=,,lnk{id}>&#xf044;</a></span>'
        hdr = ('<style>td{text-align: center;} '
            '*[href]{text-decoration: none; color: gray} '
            'table{background-color:#FFFFE0;}</style>'
            f'<table width="98%"><tr><td width="45%">modified: {mod}</td>'
            f'<td width="45%">created: {cre}</td>'
            f'<td align="right">{btn1}</td>'
            f'<td align="right">{btn2}</td></tr></table>'
        )
        return hdr

    def set_notes_data(self, data):
        logger.info('<<<<<< KU-KU >>>>>>')
        buf = []
        for row in data:
            note = ag.Note(*row)
            head = self.section_title(
                note.id,
                note.modified.strftime(time_format),
                note.created.strftime(time_format)
            )
            buf.append('\n'.join((head, note.note)))
        self.browser.setMarkdown('\n'.join(buf))

    def new_comment(self):
        self.start_edit(0)

    def ref_clicked(self, href: QUrl):
        tref = href.toString()
        logger.info(f'{tref=}')
        if tref.startswith("x,lnk"):
            if self.confirm_deletion():
                id = int(tref[5:])
                self.delete_note(id)
            return
        if tref.startswith(",,lnk"):
            id = int(tref[5:])
            self.start_edit(id)
            return
        if tref.startswith('http'):
            # TODO open link in default browser
            return
        self.set_selection(tref)

    def confirm_deletion(self):
        dlg = QMessageBox(ag.app)
        dlg.setWindowTitle('delete file note')
        dlg.setText(f'confirm deletion of note')
        dlg.setStandardButtons(QMessageBox.StandardButton.Ok |
            QMessageBox.StandardButton.Cancel)
        dlg.setIcon(QMessageBox.Icon.Question)
        return dlg.exec() == QMessageBox.StandardButton.Ok

    def delete_note(self, id: int):
        if id:
            db_ut.delete_note(self.file_id, id)
            self.set_notes_data(db_ut.get_file_notes(self.file_id))

    def start_edit(self, id: int):
        txt = db_ut.get_note(self.file_id, id) if id else ''
        logger.info(f'{id=}, {txt=}')
        self.editor.setText(txt)
        self.editor.set_note_id(id)
        self.edit_btns.show()
        self.switch_page(5)

    def set_selection(self, ref: str):
        mod = QGuiApplication.keyboardModifiers()
        i = self.tags.index(ref)
        if mod is Qt.KeyboardModifier.ControlModifier:
            if i in self.selected:
                self.selected.remove(i)
            else:
                self.selected.append(i)
        else:
            self.selected.clear()
            self.selected.append(i)

    def set_file_id(self, id: int):
        self.file_id = id
        logger.info(f'{self.file_id=}')
        self.tag_selector.set_selection(
            (int(s[0]) for s in db_ut.get_file_tagid(self.file_id))
        )
        self.tagEdit.setText(', '.join(
            self.tag_selector.get_selected()
            )
        )
        self.file_info.set_file_id(self.file_id)

    def update_tags(self, tags: list[str]):
        logger.info(f'{tags=}, {self.tagEdit.text()=}')
        def print_selected():
            for tag in tags:
                logger.info(f'{tag=}, {self.tag_selector.get_tag_id(tag)}')

        print_selected()

        self.tag_list_changed()
        self.tagEdit.setText(', '.join(tags))


    def get_selected_tag_ids(self):
        return self.tag_selector.get_selected_ids()
