from loguru import logger

from PyQt6.QtCore import Qt, QDateTime, pyqtSlot
from PyQt6.QtWidgets import (QWidget, QTextEdit, QSizePolicy,
    QMessageBox,    QVBoxLayout, QScrollArea, QAbstractScrollArea,
)

from ..core import app_globals as ag, db_ut
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


class notesContainer(QScrollArea):
    def __init__(self, editor: noteEditor, parent: QWidget=None) -> None:
        super().__init__(parent)

        self.editor = editor
        self.editing = False
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

    def is_editing(self):
        return self.editing

    def set_editing(self):
        self.editing = True

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
        self.editing = False

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
