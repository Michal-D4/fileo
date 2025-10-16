# from loguru import logger
from PyQt6.QtCore import pyqtSlot, Qt
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

        ag.author_list.list_changed.connect(self.refresh_data)

        self.br.change_selection.connect(self.update_selection)

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
        self.br.set_selection(
            (int(s[0]) for s in db_ut.get_file_author_id(self.file_id))
        )
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
        tt = tt.replace('],', '\n')
        tt = tt.replace(']', '')
        tt = tt.replace(',', '\n')
        pp = [t.strip() for t in tt.split('\n') if t.strip()]
        return pp

    def sel_list_changed(self, old: list[str], new: list[str]):
        self.remove_items(old, new)
        if self.add_items(old, new):
            self.br.set_list(db_ut.get_authors())
            ag.signals.user_signal.emit("author_inserted")

    def remove_items(self, old: list[str], new: list[str]):
        diff = set(old) - set(new)
        for d in diff:
            if id := self.br.get_tag_id(d):
                db_ut.break_file_authors_link(self.file_id, id)

    def add_items(self, old: list[str], new: list[str]) -> bool:
        def to_selected_files(a_id: int):
            if not selected_files:
                db_ut.insert_file_author(a_id, self.file_id)
                return
            for idx in selected_files:
                fileid = idx.data(Qt.ItemDataRole.UserRole)
                db_ut.insert_file_author(a_id, fileid)

        inserted = False
        diff = set(new) - set(old)
        selected_files: list = ag.file_list.selectionModel().selectedRows(0)
        for d in diff:
            if not (id := self.br.get_tag_id(d)):
                id = db_ut.insert_author(d)
                inserted = True
            to_selected_files(id)
        return inserted
