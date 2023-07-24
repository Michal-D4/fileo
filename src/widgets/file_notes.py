from loguru import logger

from PyQt6.QtCore import Qt, QDateTime, pyqtSlot
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtWidgets import (QWidget, QTextEdit, QSizePolicy,
    QMessageBox, QVBoxLayout, QScrollArea, QAbstractScrollArea,
    QMenu,
)

from ..core import app_globals as ag, db_ut, utils
from .comment import Comment


class noteEditor(QTextEdit):
    def __init__(self, parent = None) -> None:
        super().__init__(parent)
        self.note_id = 0
        self.file_id = 0
        self.branch = None

    def start_edit(self, note_id: int, file_id: int):
        self.note_id = note_id
        self.file_id = file_id
        ag.signals_.user_signal.emit(f'notes - branch request/{file_id}')

    def set_branch(self, branch):
        self.branch = branch

    def get_file_id(self) -> int:
        return self.file_id

    def get_note_id(self) -> int:
        return self.note_id

    def get_branch(self) -> str:
        return ','.join((str(it) for it in self.branch))

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

    def go_menu(self, e: QMouseEvent):
        if e.buttons() == Qt.MouseButton.RightButton:
            logger.info(f'{self.editor.get_file_id()=}, {self.file_id=}')
            if self.editor.get_file_id() == self.file_id:
                return
            menu = QMenu(ag.app)
            menu.addAction('Go to file')
            act = menu.exec(ag.app.ui.edited_file.mapToGlobal(e.pos()))
            if act:
                self.go_action(act.text())

    def go_action(self, act_text: str):
        file_id = self.editor.get_file_id()
        branch = self.editor.get_branch()
        ag.signals_.user_signal.emit(
            f"file-note: {act_text}/{file_id}-{branch}"
        )

    def is_editing(self):
        return self.editing

    def set_editing(self, state: bool):
        self.editing = state
        self.edited_file_in_statusbar(state)

    def edited_file_in_statusbar(self, show: bool):
        if show:
            file_id = self.editor.get_file_id()
            filename = db_ut.get_file_name(file_id)
            ag.app.ui.edited_file.setText(filename)
            ag.app.ui.edited_file.setEnabled(True)
            ag.app.ui.edited_file.mousePressEvent = self.go_menu
        else:
            ag.app.ui.edited_file.clear()
            ag.app.ui.edited_file.setEnabled(False)

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

    @pyqtSlot(int, int)
    def remove_item(self, note_id: int, file_id: int):
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
