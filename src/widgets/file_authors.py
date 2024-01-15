
from loguru import logger

from PyQt6.QtCore import QSize, pyqtSlot
from PyQt6.QtWidgets import (QWidget,
    QVBoxLayout, QFrame, QLineEdit,
)

from ..core.compact_list import aBrowser
from ..core import app_globals as ag, db_ut


class authorBrowser(QWidget):
    def __init__(self, editor: QLineEdit, parent=None) -> None:
        super().__init__(parent)
        self.file_id = 0
        self.editor = editor

        self.setup_ui()

        # list of authors changed outside, in ag.author_list
        ag.author_list.edit_finished.connect(self.refresh_data)

        self.br.change_selection.connect(self.update_selection)

    def setup_editor(self):
        self.editor.setText(self.set_selected_text())

    def setup_ui(self):
        self.br = aBrowser(brackets=True)
        self.br.setObjectName('author_selector')

        authors = QFrame(self)
        authors.setObjectName('authors')
        f_layout = QVBoxLayout(self)
        f_layout.setContentsMargins(0, 0, 0, 0)

        m_layout = QVBoxLayout(authors)
        m_layout.setContentsMargins(0, 0, 0, 0)
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
        self.editor.setText(', '.join(
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
        self.editor.setText(', '.join(txt))

    def get_edited_list(self) -> list[str]:
        tt = self.editor.text().strip()
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
        self.remove_items(old, new)
        self.add_items(old, new)

    def remove_items(self, old: list[str], new: list[str]):
        diff = set(old) - set(new)
        for d in diff:
            if id := self.br.get_tag_id(d):
                db_ut.break_file_authors_link(self.file_id, id)

    def add_items(self, old: list[str], new: list[str]):
        inserted = False
        diff = set(new) - set(old)
        for d in diff:
            if db_ut.add_author(self.file_id, d):
                inserted = True
        if inserted:
            self.set_authors()
            ag.signals_.user_signal.emit("author_inserted")
