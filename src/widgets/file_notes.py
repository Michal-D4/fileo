# from loguru import logger

from PyQt6.QtCore import Qt, QDateTime, pyqtSlot
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtWidgets import (QWidget, QSizePolicy, QMessageBox,
    QVBoxLayout, QScrollArea, QAbstractScrollArea,
)

from ..core import app_globals as ag, db_ut
from .file_note import fileNote
from .note_editor import noteEditor


class notesContainer(QScrollArea):
    def __init__(self, editor: noteEditor, parent: QWidget=None) -> None:
        super().__init__(parent)

        self.editor = editor
        self.editing = False
        self.set_ui()

        self.file_id = 0

        ag.signals_.delete_note.connect(self.remove_item)
        ag.signals_.refresh_note_list.connect(self.set_notes_data)
        ag.signals_.color_theme_changed.connect(self.theme_changed)

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
        self.scroll_layout = QVBoxLayout(self.scrollWidget)
        self.scroll_layout.setContentsMargins(0,0,0,0)
        self.scroll_layout.setSpacing(2)
        self.scroll_layout.setObjectName('scroll_layout')
        self.scrollWidget.setLayout(self.scroll_layout)
        self.setWidget(self.scrollWidget)
        self.scroll_layout.addStretch(1)
        self.setStyleSheet("border: none;")

    def go_menu(self, e: QMouseEvent):
        if e.buttons() == Qt.MouseButton.LeftButton:
            self.go_to_file()

    def go_to_file(self):
        file_id = self.editor.get_file_id()
        ag.signals_.user_signal.emit(f"file-note: Go to file\\{file_id}")

    def is_editing(self):
        return self.editing

    def set_editing(self, state: bool):
        # logger.info(f'{state=}')
        self.editing = state
        ag.app.ui.edited_file.setEnabled(state)
        if state:
            file_id = self.editor.get_file_id()
            filename = db_ut.get_file_name(file_id)
            ag.app.ui.edited_file.setText(filename)
        else:
            ag.app.ui.edited_file.clear()

    def set_file_id(self, file_id: int):
        self.file_id = db_ut.get_file_id_to_notes(file_id)
        self.set_notes_data()

    def get_file_id(self):
        return self.file_id

    def set_notes_data(self):
        def add_to_top(item: fileNote):
            item.setSizePolicy(
                QSizePolicy.Policy.Preferred,
                QSizePolicy.Policy.MinimumExpanding
            )
            self.scroll_layout.insertWidget(0, item)

        self.setUpdatesEnabled(False)
        ag.note_buttons.clear()
        self.clear_layout()
        for row in db_ut.get_file_notes(self.file_id):
            note = fileNote(*row[1:])
            note.set_text(row[0])
            note.add_buttons()
            add_to_top(note)
        self.collapse()
        self.show_first_note()
        self.setUpdatesEnabled(True)
        self.show()

    def show_first_note(self):
        item = self.scroll_layout.itemAt(0)
        if item.widget():
            note: fileNote = item.widget()
            note.ui.collapse.setChecked(False)
            note.view_note()

    def theme_changed(self):
        for i in reversed(range(self.scroll_layout.count())):
            item = self.scroll_layout.itemAt(i)
            if item.widget():
                note: fileNote = item.widget()
                if not note.ui.collapse.isChecked():
                    note.set_browser_text()

    def clear_layout(self):
        for i in reversed(range(self.scroll_layout.count()-1)):
            item = self.scroll_layout.takeAt(i)
            if item.widget():
                item.widget().deleteLater()

    def finish_editing(self):
        self.update_note()
        self.editing = False

    def update_note(self):
        def compare_hashes(file1: int, file2: int) -> bool:
            return (
                file1 == file2 or
                db_ut.get_file_hash(file1) == db_ut.get_file_hash(file2)
            )

        note: fileNote = self.editor.get_note()
        file_id = note.get_file_id()
        note_id = note.get_note_id()
        txt = self.editor.get_text()

        if note_id:
            ts = db_ut.update_note(file_id, note_id, txt)
        else:
            ts = db_ut.insert_note(file_id, txt)

        ag.add_recent_file(file_id)

        if compare_hashes(self.file_id, file_id):
            self.update_date_in_file_list(ts)
            self.set_notes_data()

    def update_date_in_file_list(self, ts: int):
        if ts > 0:
            last_note_date = QDateTime()
            last_note_date.setSecsSinceEpoch(ts)
            ag.file_list.model().update_field_by_name(
                last_note_date, "Date of last note",
                ag.file_list.currentIndex()
            )

    @pyqtSlot(fileNote)
    def remove_item(self, note: fileNote):
        file_id = note.get_file_id()
        note_id = note.get_note_id()

        if (self.editing and
            self.editor.get_note_id() == note_id and
            self.editor.get_file_id() == file_id):
            ag.show_message_box(
                'Note is editing now',
                "The note can't be deleted right now.",
                icon=QMessageBox.Icon.Warning,
                details="It is editing!"
            )
            return

        if ag.show_message_box(
            'delete file note',
            'confirm deletion of note',
            btn=QMessageBox.StandardButton.Ok |
            QMessageBox.StandardButton.Cancel,
            icon=QMessageBox.Icon.Question
        ) == QMessageBox.StandardButton.Ok:
            self.scroll_layout.removeWidget(note)
            note.deleteLater()
            db_ut.delete_note(file_id, note_id)

    def collapse(self):
        if self.scroll_layout.count() <= 1:
            return

        for i in reversed(range(self.scroll_layout.count()-1)):
            item = self.scroll_layout.itemAt(i)
            if item.widget():
                note: fileNote = item.widget()
                note.ensure_collapsed()
