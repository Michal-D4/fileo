# from loguru import logger
from enum import Enum, unique

from PyQt6.QtCore import QPoint, Qt
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
from .srch_in_notes import srchInNotes
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

        authors_ttl = tug.qss_params['$FoldTitles'].split(',')[-1]
        self.set_author_title(authors_ttl)

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
        ag.signals_.author_widget_title.connect(self.set_author_title)

        self.set_buttons()

        self.tagEdit.editingFinished.connect(self.tag_selector.finish_edit_tag)

        self.l_file_notes_press(None)

        self.l_tags.mousePressEvent = self.l_tags_press
        self.l_authors.mousePressEvent = self.l_authors_press
        self.l_locations.mousePressEvent = self.l_locations_press
        self.l_file_info.mousePressEvent = self.l_file_info_press
        self.l_file_notes.mousePressEvent = self.l_file_notes_press
        self.l_editor.mousePressEvent = self.l_editor_press

    def set_author_title(self, ttl: str):
        self.l_authors.setText(f"{ttl[:-1]} selector")
        self.authorEdit.setToolTip(f"File\'s {ttl.lower()}")
        self.authorEdit.setPlaceholderText(
            f'Enter a list of {ttl.lower()} separated by commas or select from the "{ttl[:-1]} selector"'
        )

    def set_buttons(self):

        self.expand.setIcon(tug.get_icon("up"))
        self.expand.clicked.connect(self.toggle_collapse)

        self.srch_in_notes.setIcon(tug.get_icon("search"))
        self.srch_in_notes.clicked.connect(self.srch_notes)
        ctrl_f = QShortcut(QKeySequence("Ctrl+F"), self)
        ctrl_f.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        ctrl_f.activated.connect(self.srch_notes)

        self.plus.setIcon(tug.get_icon("plus"))
        self.plus.clicked.connect(self.new_file_note)
        ctrl_n = QShortcut(QKeySequence("Ctrl+N"), self)
        ctrl_n.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        ctrl_n.activated.connect(self.new_file_note)

        self.collapse_notes.setIcon(tug.get_icon("collapse_notes"))
        self.collapse_notes.clicked.connect(self.notes.collapse)

        self.save.setIcon(tug.get_icon("ok"))
        self.save.clicked.connect(self.save_note)
        self.save.setShortcut(QKeySequence("Ctrl+S"))

        self.cancel.setIcon(tug.get_icon("cancel2"))
        self.cancel.clicked.connect(self.cancel_note_editing)
        self.cancel.setShortcut("Ctrl+Q")

        self.edit_btns.hide()
        ag.buttons.append((self.expand, "up", "down3"))
        ag.buttons.append((self.srch_in_notes, "search"))
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
        if self.cur_page is not Page.INFO:
            self.l_file_info.setToolTip('copy file info by press "Right button + Shift"')
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
        ag.add_recent_file(self.file_id)
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

        if self.cur_page is Page.INFO:
            self.l_file_info.setToolTip("")

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

    def srch_notes(self):
        if "srchInNotes" in ag.popups:
            return
        sn = srchInNotes(self)
        sn.move(self.srch_in_notes.pos() - QPoint(sn.width(), -10))
        sn.show()
        sn.srch_pattern.setFocus()

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

    def new_file_note(self):
        file_id = self.notes.get_file_id()
        if not file_id:
            return
        self.start_edit(fileNote(file_id, 0))

    def start_edit(self, note: fileNote):
        def call_back():
            self.edit_btns.show()
            self.switch_page(Page.EDIT)

        if self.notes.is_editing():
            ag.show_message_box(
                "There is an active editor",
                "Only one note editor can be opened at a time",
                callback=call_back
            )
            return
        self.editor.start_edit(note)
        self.show_editor()

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
                note.get_file_id(),
                note.get_note_id(),
                self.editor.get_text(),
            )
        return get_attributes() if self.notes.is_editing() else (False,)

    def set_edit_state(self, vals: tuple):
        if not vals[0]:
            self.cancel_note_editing()
            return
        note = fileNote(vals[1], vals[2])   # file_id, note_id
        self.editor.set_note(note)
        self.editor.set_text(vals[3])
        self.show_editor()

    def set_data(self, file_id: int):
        # logger.info(f'{file_id=}')
        self.file_id = file_id

        self.tag_selector.set_file_id(file_id)
        self.author_selector.set_file_id(file_id)
        self.file_info.set_file_id(file_id)
        self.notes.set_file_id(file_id)
        self.locator.set_data(file_id)
