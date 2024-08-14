from loguru import logger

from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import QLineEdit

from ..core.compact_list import aBrowser
from ..core import app_globals as ag, db_ut
from .. import tug

class tagBrowser(aBrowser):
    def __init__(self, editor: QLineEdit, parent=None) -> None:
        super().__init__(parent)
        self.file_id = 0
        self.editor = editor
        ag.signals_.color_theme_changed.connect(self.show_in_bpowser)

    def show_in_bpowser(self):
        self.browser.clear()
        css = tug.get_dyn_qss('browser_style')
        self.browser.setText(''.join((css, self.html_selected())))

    def html_selected(self):
        sel = self.sel_tags
        inn = ' '.join(f"<a class={'s' if tag in sel else 't'} href=#{tag}>{tag}</a> "
             for tag in self.tags)
        return inn

    @pyqtSlot(list)
    def update_tags(self, tags: list[str]):
        self.tag_list_changed(self.editor_tag_list(), tags)
        self.editor.setText(', '.join(tags))

    def tag_list_changed(self, old: list[str], new: list[str]):
        self.remove_tags(old, new)
        if self.add_tags(old, new):
            self.update_tag_list()
            ag.signals_.user_signal.emit("tag_inserted")

    def remove_tags(self, old: list[str], new: list[str]):
        diff = set(old) - set(new)
        for d in diff:
            id = self.get_tag_id(d)
            db_ut.delete_tag_file(id, self.file_id)

    def add_tags(self, old, new) -> bool:
        inserted = False
        diff = set(new) - set(old)
        for d in diff:
            if not (id := self.get_tag_id(d)):
                id = db_ut.insert_tag(d)
                inserted = True
            db_ut.insert_tag_file(id, self.file_id)
        return inserted

    @pyqtSlot()
    def update_tag_list(self):
        self.set_list(db_ut.get_tags())

    @pyqtSlot()
    def finish_edit_tag(self):
        old = self.get_selected()
        new = self.editor_tag_list()
        self.tag_list_changed(old, new)

    def editor_tag_list(self):
        """
        tag can't contain blanks and can't be empty string
        """
        tmp = self.editor.text().replace(' ','')
        return [t for t in tmp.split(',') if t]

    def set_selected_text(self):
        self.editor.setText(
            ', '.join(self.get_selected())
        )

    def set_file_id(self, id: int):
        self.file_id = id
        self.set_selection(
            (int(s[0]) for s in db_ut.get_file_tagid(id))
        )
        self.set_selected_text()
