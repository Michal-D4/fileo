from loguru import logger
from enum import Enum, unique

from PyQt6.QtCore import QTimer, pyqtSlot
from PyQt6.QtGui import QMouseEvent, QKeySequence, QShortcut
from PyQt6.QtWidgets import QWidget, QStackedWidget

from .ui_notes import Ui_FileNotes

from ..core import app_globals as ag, db_ut
from .file_authors import authorBrowser
from .file_info import fileInfo
from .file_notes import notesContainer
from .file_note import fileNote
from .file_tags import tagBrowser
from .locations import Locations
from .note_editor import noteEditor
from .. import tug

@unique
class Page(Enum):
    TAGS = 0
    AUTHORS = 1
    LOCS = 2
    INFO = 3
    NOTE = 4
    EDIT = 5


class fileDataHolder(QWidget, Ui_FileNotes):
    def __init__(self, parent = None) -> None:
        super().__init__(parent)
        self.file_id = 0
        self.s_height = 0

        self.setupUi(self)

        self.page_selectors = {
            Page.TAGS: self.l_tags,
            Page.AUTHORS: self.l_authors,
            Page.LOCS: self.l_locations,
            Page.INFO: self.l_file_info,
            Page.NOTE: self.l_file_notes,
            Page.EDIT: self.l_editor,
        }

        self.set_pages()
        self.cur_page: Page = Page.TAGS

        self.l_editor.hide()

        ag.signals_.start_edit_note.connect(self.start_edit)

        self.set_buttons()

        self.tagEdit.editingFinished.connect(self.tag_selector.finish_edit_tag)

        self.l_file_notes_press(None)

        self.l_tags.mousePressEvent = self.l_tags_press
        self.l_authors.mousePressEvent = self.l_authors_press
        self.l_locations.mousePressEvent = self.l_locations_press
        self.l_file_info.mousePressEvent = self.l_file_info_press
        self.l_file_notes.mousePressEvent = self.l_file_notes_press
        self.l_editor.mousePressEvent = self.l_editor_press

    def set_buttons(self):

        self.expand.setIcon(tug.get_icon("up"))
        self.expand.clicked.connect(self.toggle_collapse)

        self.plus.setIcon(tug.get_icon("plus"))
        self.plus.clicked.connect(self.new_file_note)
        ctrl_n = QShortcut(QKeySequence("Ctrl+n"), self)
        ctrl_n.activated.connect(self.short_new_note)

        self.collapse_notes.setIcon(tug.get_icon("collapse_notes"))
        self.collapse_notes.clicked.connect(self.notes.collapse_all)

        self.save.setIcon(tug.get_icon("ok"))
        self.save.clicked.connect(self.save_note)
        ctrl_s = QShortcut(QKeySequence("Ctrl+s"), self)
        ctrl_s.activated.connect(self.save_note)

        self.cancel.setIcon(tug.get_icon("cancel2"))
        self.cancel.clicked.connect(self.cancel_note_editing)
        ctrl_q = QShortcut(QKeySequence("Ctrl+q"), self)
        ctrl_q.activated.connect(self.short_cancel_editing)

        self.edit_btns.hide()
        ag.buttons.append((self.expand, "up", "down3"))
        ag.buttons.append((self.plus, "plus"))
        ag.buttons.append((self.collapse_notes, "collapse_notes"))
        ag.buttons.append((self.save, "ok"))
        ag.buttons.append((self.cancel, "cancel2"))

    def set_pages(self):
        self.pages = QStackedWidget(self)
        self.pages.setObjectName("pages")

        # add tag selector page (0)
        self.tag_selector = tagBrowser(self.tagEdit)
        self.pages.addWidget(self.tag_selector)
        self.tag_selector.setObjectName('tag_selector')
        self.tag_selector.change_selection.connect(self.tag_selector.update_tags)
        ag.tag_list.list_changed.connect(self.tag_selector.update_tag_list)

        # add author selector page (1)
        self.author_selector = authorBrowser(self.authorEdit)
        self.pages.addWidget(self.author_selector)
        self.author_selector.setObjectName('author_selector')
        self.authorEdit.editingFinished.connect(self.author_selector.finish_edit_list)
        self.authorEdit.hide()

        # add file locations page (2)
        self.locator = Locations()
        self.pages.addWidget(self.locator)
        self.locator.setObjectName('locator')

        # add file info page (3)
        self.file_info = fileInfo()
        self.file_info.setObjectName('file_info')
        self.pages.addWidget(self.file_info)

        self.editor = noteEditor()
        self.editor.setObjectName('note_editor')

        self.notes = notesContainer(self.editor)
        self.notes.setObjectName('notes_container')
        ag.app.ui.edited_file.mousePressEvent = self.notes.go_menu

        # add file notes page (4)
        self.pages.addWidget(self.notes)
        # add note editor page (5)
        self.pages.addWidget(self.editor)

        self.passive_style()

        self.main_layout.addWidget(self.pages)

    def passive_style(self):
        ss = tug.get_dyn_qss('passive_selector')
        for lbl in self.page_selectors.values():
            lbl.setStyleSheet(ss)

    def cur_page_restyle(self):
        self.page_selectors[self.cur_page].setStyleSheet(
            tug.get_dyn_qss('active_selector')
        )

    def l_tags_press(self, e: QMouseEvent):
        self.tagEdit.setReadOnly(False)
        self.tagEdit.setStyleSheet(tug.get_dyn_qss("line_edit"))
        self.tag_selector.set_selected_text()
        self.switch_page(Page.TAGS)

    def l_authors_press(self, e: QMouseEvent):
        self.tagEdit.hide()
        self.authorEdit.show()
        self.author_selector.set_selected_text()
        self.switch_page(Page.AUTHORS)

    def l_locations_press(self, e: QMouseEvent):
        self.switch_page(Page.LOCS)

    def l_file_info_press(self, e: QMouseEvent):
        self.switch_page(Page.INFO)

    def l_file_notes_press(self, e: QMouseEvent):
        if self.file_id:
            self.note_btns.show()
        self.switch_page(Page.NOTE)

    def l_editor_press(self, e: QMouseEvent):
        self.edit_btns.show()
        self.switch_page(Page.EDIT)

    def switch_page(self, new_page: Page):
        if new_page is self.cur_page:
            return
        ag.add_file_to_recent(self.file_id)
        # logger.info(f'{self.cur_page.name=}, {new_page.name=}')

        self.page_selectors[self.cur_page].setStyleSheet(
            tug.get_dyn_qss('passive_selector')
        )
        self.page_selectors[new_page].setStyleSheet(
            tug.get_dyn_qss('active_selector')
        )

        if self.cur_page is Page.NOTE:
            self.note_btns.hide()

        if self.cur_page is Page.EDIT:
            self.edit_btns.hide()

        if self.cur_page is Page.TAGS:
            self.tagEdit.setReadOnly(True)
            self.tagEdit.setStyleSheet(tug.get_dyn_qss("line_edit_ro"))

        if self.cur_page is Page.AUTHORS:
            self.authorEdit.hide()
            self.tagEdit.show()

        self.cur_page = new_page
        self.pages.setCurrentIndex(new_page.value)

    def toggle_collapse(self):
        if self.expand.isChecked():
            self.s_height = self.height()
            self.expand.setIcon(tug.get_icon("down3"))
            hh = ag.file_list.height() + self.s_height
            ag.app.ui.noteHolder.setMinimumHeight(hh)
            ag.app.ui.noteHolder.setMaximumHeight(hh)
            ag.file_list.hide()
        else:
            self.expand.setIcon(tug.get_icon("up"))
            ag.app.ui.noteHolder.setMinimumHeight(self.s_height)
            ag.app.ui.noteHolder.setMaximumHeight(self.s_height)
            ag.file_list.show()

    def short_cancel_editing(self):
        if not self.notes.is_editing():
            return
        self.cancel_note_editing()

    def cancel_note_editing(self):
        # logger.info(f'{self.cur_page.name=}')
        self.l_editor.hide()
        self.notes.set_editing(False)
        self.l_file_notes_press(None)

    def save_note(self):
        if self.notes.is_editing():
            self.notes.finish_editing()
            self.l_editor.hide()
            self.notes.set_editing(False)
            self.l_file_notes_press(None)

    def set_tag_author_data(self):
        self.tag_selector.set_list(db_ut.get_tags())
        self.author_selector.set_authors()

    def short_new_note(self):
        if ag.app.focusWidget() is self.notes:
            self.new_file_note()

    def new_file_note(self):
        if not self.file_id:
            return
        self.start_edit(fileNote(self.file_id, 0))

    def start_edit(self, note: fileNote):
        # logger.info(f'editing: {self.notes.is_editing()}')
        if self.notes.is_editing():
            self.is_edit_message()
            self.edit_btns.show()
            self.switch_page(Page.EDIT)
            return
        self.editor.start_edit(note)
        self.show_editor()

    def is_edit_message(self):
        @pyqtSlot()
        def restore_file_edited():
            ag.app.ui.edited_file.setText(file_edited)
            ag.app.ui.edited_file.setStyleSheet(tug.get_dyn_qss('edit_message', 1))

        file_edited = ag.app.ui.edited_file.text()
        ag.app.ui.edited_file.setStyleSheet(tug.get_dyn_qss('edit_message'))
        ag.app.ui.edited_file.setText("Only one note editor can be opened at a time")
        QTimer.singleShot(3000, restore_file_edited)

    def show_editor(self):
        self.notes.set_editing(True)
        self.edit_btns.show()
        self.l_editor.show()
        self.switch_page(Page.EDIT)
        self.editor.note_editor.setFocus()

    def get_edit_state(self) -> tuple:
        def get_attributes():
            note: fileNote = self.editor.get_note()
            return (
                True,
                note.get_note_file_id(),
                note.get_note_id(),
                note.get_file_id(),
                self.editor.get_branch(),
                self.editor.get_text(),
            )
        return get_attributes() if self.notes.is_editing() else (False,)

    def set_edit_state(self, vals: tuple):
        if not vals[0]:
            self.cancel_note_editing()
            return
        note = fileNote(vals[1], vals[2])
        note.set_file_id(vals[3])
        self.editor.set_note(note)
        self.editor.set_branch(vals[4])
        self.editor.set_text(vals[5])
        self.show_editor()

    def set_data(self, file_id: int, branch: list):
        # logger.info(f'{file_id=}')
        self.file_id = file_id

        self.tag_selector.set_file_id(file_id)
        self.author_selector.set_file_id(file_id)
        self.file_info.set_file_id(file_id)
        self.notes.set_file_id(file_id)

        self.locator.set_data(file_id, branch)
        # locator calculates all branches the file belongs to
        if not branch:
            branch = self.locator.get_branch(file_id)
        if not self.notes.is_editing():
            self.editor.set_branch(branch)
