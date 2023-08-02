from loguru import logger

from PyQt6.QtCore import pyqtSlot
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtWidgets import QWidget, QStackedWidget

from .ui_notes import Ui_FileNotes

from ..core import icons, app_globals as ag, db_ut
from .file_authors import authorBrowser
from .file_info import fileInfo
from .file_notes import noteEditor, notesContainer
from .file_tags import tagBrowser
from .locations import Locations


class fileDataHolder(QWidget, Ui_FileNotes):
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
            self.l_file_notes, self.l_editor,
        ]
        self.set_stack_pages()
        self.l_editor.hide()

        ag.signals_.start_edit_note.connect(self.start_edit)

        self.expand.setIcon(icons.get_other_icon("up"))
        self.expand.clicked.connect(self.up_down)

        self.plus.setIcon(icons.get_other_icon("plus"))
        self.plus.clicked.connect(self.new_file_note)

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
        self.l_file_notes_press(None)

        self.l_tags.mousePressEvent = self.l_tags_press
        self.l_authors.mousePressEvent = self.l_authors_press
        self.l_locations.mousePressEvent = self.l_locations_press
        self.l_file_info.mousePressEvent = self.l_file_info_press
        self.l_file_notes.mousePressEvent = self.l_file_notes_press
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

        # add file notes page (4)
        self.stackedWidget.addWidget(self.notes)
        # add note editor page (5)
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

    def l_file_notes_press(self, e: QMouseEvent):
        # file notes page
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

    def set_branch(self, branch):
        if not self.notes.is_editing():
            self.editor.set_branch(branch)
        self.locator.set_current_branch(branch)

    def cancel_note_editing(self):
        self.l_editor.hide()
        self.notes.set_editing(False)
        self.l_file_notes_press(None)

    def note_changed(self):
        self.notes.finish_editing()
        self.l_editor.hide()
        self.notes.set_editing(False)
        self.l_file_notes_press(None)

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

    def new_file_note(self):
        if self.notes.is_editing():
            self.switch_page(5)
            return
        self.show_editor(0, self.file_id, '')

    def start_edit(self, note_id: int, file_id: int):
        if self.notes.is_editing():
            self.switch_page(5)
            return

        txt = db_ut.get_note(file_id, note_id)
        self.show_editor(note_id, file_id, txt)

    def show_editor(self, note_id: int, file_id: int, txt: str):
        self.editor.start_edit(note_id, file_id)
        self.editor.setText(txt)

        self.notes.set_editing(True)

        self.note_btns.hide()
        self.edit_btns.show()
        self.l_editor.show()
        self.switch_page(5)
        self.editor.setFocus()

    def set_file_id(self, id: int):
        self.file_id = id
        self.tag_selector.set_selection(
            (int(s[0]) for s in db_ut.get_file_tagid(id))
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
