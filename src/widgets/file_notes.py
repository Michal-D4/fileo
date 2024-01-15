from loguru import logger

from PyQt6.QtCore import Qt, QDateTime, pyqtSlot
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtWidgets import (QWidget, QSizePolicy, QMessageBox,
    QVBoxLayout, QScrollArea, QAbstractScrollArea, QMenu,
)

from ..core import app_globals as ag, db_ut, utils
from .file_note import fileNote
from .note_editor import noteEditor


class notesContainer(QScrollArea):
    def __init__(self, editor: noteEditor, parent: QWidget=None) -> None:
        super().__init__(parent)

        self.editor = editor
        self.editing = False
        self.ini = True
        self.set_ui()

        self.file_id = 0

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
        self.scroll_layout.setContentsMargins(9,0,6,0)
        self.scroll_layout.setSpacing(6)
        self.scroll_layout.setObjectName('scroll_layout')
        self.setStyleSheet("border: none;")

    def go_menu(self, e: QMouseEvent):
        if e.buttons() == Qt.MouseButton.LeftButton:
            self.go_to_file()

    def go_to_file(self):
        file_id = self.editor.get_file_id()
        branch = ','.join((str(i) for i in self.editor.get_branch()))
        # logger.info(f'{branch=}')
        ag.signals_.user_signal.emit(
            f"file-note: Go to file\\{file_id}-{branch}"
        )

    def is_editing(self):
        return self.editing

    def set_editing(self, state: bool):
        # logger.info(f'{state=}')
        self.editing = state
        if state:
            self.edited_file_in_status(state)

    def edited_file_in_status(self, show: bool):
        # logger.info(f'{show=}')
        if show:
            file_id = self.editor.get_file_id()
            filename = db_ut.get_file_name(file_id)
            ag.app.ui.edited_file.setText(filename)
            ag.app.ui.edited_file.setEnabled(True)
            ag.app.ui.edited_file.mousePressEvent = self.go_menu
        else:
            ag.app.ui.edited_file.clear()
            ag.app.ui.edited_file.setEnabled(False)

    def set_file_id(self, file_id: int):
        self.file_id = file_id
        self.set_notes_data()

    def set_notes_data(self):
        self.setUpdatesEnabled(False)
        self.clear_layout()
        self.scroll_layout.addStretch(1)
        if self.ini:
            self.ini = False
            self.setUpdatesEnabled(True)
            return
        data = db_ut.get_file_notes(self.file_id)
        for row in data:
            note = fileNote(*row[1:], self.file_id)
            note.set_text(row[0])
            self.add_item(note)
        self.setUpdatesEnabled(True)

    def clear_layout(self):
        for i in reversed(range(self.scroll_layout.count())):
            item = self.scroll_layout.takeAt(i)
            if item.widget():
                item.widget().deleteLater()

    def add_item(self, item: fileNote):
        item.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.MinimumExpanding
        )
        self.scroll_layout.insertWidget(0, item)

    def finish_editing(self):
        self.update_note()
        self.editing = False

    def update_note(self):
        note: fileNote = self.editor.get_note()
        note_file_id = note.get_note_file_id()
        note_id = note.get_note_id()
        txt = self.editor.get_text()

        if note_id:
            ts = db_ut.update_note(note_file_id, note_id, txt)
        else:
            ts = db_ut.insert_note(note_file_id, txt)

        file_id = note.get_file_id()
        ag.add_history_file(file_id)

        if self.file_id == file_id:
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
            utils.show_message_box(
                'Note is editing now',
                "The note can't be deleted right now.",
                icon=QMessageBox.Icon.Warning,
                details="It is editing!"
            )
            return

        if utils.show_message_box(
            'delete file note',
            'confirm deletion of note',
            btn=QMessageBox.StandardButton.Ok |
            QMessageBox.StandardButton.Cancel,
            icon=QMessageBox.Icon.Question
        ) == QMessageBox.StandardButton.Ok:
            self.scroll_layout.removeWidget(note)
            note.deleteLater()
            db_ut.delete_note(file_id, note_id)

    def collapse_all(self):
        for i in reversed(range(self.scroll_layout.count())):
            item = self.scroll_layout.itemAt(i)
            if item.widget():
                item.widget().check_collapse_button()
