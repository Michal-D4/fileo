# from loguru import logger

from PyQt6.QtCore import Qt, QDateTime, pyqtSlot, QTimer
from PyQt6.QtGui import QMouseEvent, QTextCursor
from PyQt6.QtWidgets import (QWidget, QSizePolicy, QMessageBox,
    QVBoxLayout, QScrollArea, QAbstractScrollArea, QStyle,
)

from ..core import app_globals as ag, db_ut
from .file_note import fileNote, Direction
from .note_editor import noteEditor
from .srch_in_notes import srchInNotes
from .cust_msgbox import show_message_box


class notesContainer(QScrollArea):
    def __init__(self, editor: noteEditor, parent: QWidget=None) -> None:
        super().__init__(parent)

        self.editor = editor
        self.editing = False
        self.set_ui()

        self.file_id = 0
        self.ids = []

        ag.signals.delete_note.connect(self.remove_item)
        ag.signals.refresh_note_list.connect(self.set_notes_data)
        ag.signals.color_theme_changed.connect(self.theme_changed)

    def set_ui(self):
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.setWidgetResizable(True)
        self.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.setStyleSheet("border: none;")

    def set_scroll_widget(self):
        scrollWidget = QWidget()
        scrollWidget.setObjectName("scrollWidget")
        self.scroll_layout = QVBoxLayout(scrollWidget)
        self.scroll_layout.setContentsMargins(0,0,0,0)
        self.scroll_layout.setSpacing(2)
        self.scroll_layout.setObjectName('scroll_layout')
        self.setWidget(scrollWidget)
        self.scroll_layout.addStretch(1)
        fileNote.set_current_note(None)
        self.ids.clear()

    def set_search_object(self, obj: srchInNotes):
        obj.next_btn.clicked.connect(self.go_next_match)
        obj.prev_btn.clicked.connect(self.go_prev_match)
        self.search_obj = obj

    def go_menu(self, e: QMouseEvent):
        if e.buttons() == Qt.MouseButton.LeftButton:
            self.go_to_file()

    def go_to_file(self):
        file_id = self.editor.get_file_id()
        ag.signals.user_signal.emit(f"file-note: Go to file\\{file_id}")

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

    def set_notes_data(self, plain: bool=False):
        def add_to_top(note: fileNote):
            note.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.MinimumExpanding)
            self.scroll_layout.insertWidget(0, note)
            self.ids.insert(0, note.note_id)

        self.setUpdatesEnabled(False)
        self.set_scroll_widget()
        ag.note_buttons.clear()
        for row in db_ut.get_file_notes(self.file_id):
            note = fileNote(*row[1:])  # except note text
            note.set_text(row[0], plain)
            note.add_buttons()
            add_to_top(note)
        self.collapse_all()
        self.show_first_note(plain)
        self.setUpdatesEnabled(True)
        self.show()

    def show_first_note(self, plain: bool):
        if ag.mode is ag.appMode.FOUND_IN_NOTES:
            if self.find_in_next_note(0):
                self.search_obj.next_btn.setEnabled(True)
            elif not plain:
                self.set_notes_data(plain=True)
            return
        item = self.scroll_layout.itemAt(0)
        if item.widget():
            note: fileNote = item.widget()
            note.ui.collapse.setChecked(False)

    def find_in_next_note(self, beg: int) -> bool:
        for i in range(beg, self.scroll_layout.count()):
            item = self.scroll_layout.itemAt(i)
            note: fileNote = item.widget()
            if isinstance(note, fileNote):
                note.set_cursor_position(QTextCursor.MoveOperation.Start)
                if note.find_pattern() > -1:
                    self.switch_note(note)
                    return True
        return False

    def find_in_prev_note(self) -> bool:
        for i in reversed(range(self.ids.index(fileNote.current_note.note_id))):
            item = self.scroll_layout.itemAt(i)
            note: fileNote = item.widget()
            note.set_cursor_position()
            if note and note.find_pattern(direction=Direction.Prev) > -1:
                self.switch_note(note)
                return True
        return False

    def switch_note(self, note: fileNote) -> bool:
        if fileNote.current_note:
            fileNote.current_note.ui.collapse.setChecked(True)
        fileNote.set_current_note(note)
        fileNote.current_note.ui.collapse.setChecked(False)

    @pyqtSlot()
    def go_next_match(self):
        pos = fileNote.current_note.find_pattern()
        if pos == -1:
            if not self.find_in_next_note(self.ids.index(fileNote.current_note.note_id)+1):
                self.search_obj.next_btn.setEnabled(False)
                return
        self.search_obj.prev_btn.setEnabled(True)
        QTimer.singleShot(25, self.scroll_to_current_pos)

    @pyqtSlot()
    def go_prev_match(self):
        pos = fileNote.current_note.find_pattern(direction=Direction.Prev)
        if pos == -1:
            if not self.find_in_prev_note():
                self.search_obj.prev_btn.setEnabled(False)
                return
        self.search_obj.next_btn.setEnabled(True)
        QTimer.singleShot(25, self.scroll_to_current_pos)

    def scroll_to_current_pos(self):
        note = fileNote.current_note
        pos = note.mapToParent(note.cursor_location())
        self.ensureVisible(pos.x(), pos.y(), xMargin=50, yMargin=100)

    def theme_changed(self):
        for i in reversed(range(self.scroll_layout.count())):
            item = self.scroll_layout.itemAt(i)
            if item.widget():
                note: fileNote = item.widget()
                if not note.ui.collapse.isChecked():
                    note.set_browser_text()

    def finish_editing(self):
        note: fileNote = self.editor.get_note()
        file_id = note.get_file_id()
        note_id = note.get_note_id()
        txt = self.editor.get_text()

        if note_id:
            ts = db_ut.update_note(file_id, note_id, txt)
        else:
            ts = db_ut.insert_note(file_id, txt)

        ag.add_recent_file(file_id)
        if self.file_id == file_id or db_ut.get_file_hash(self.file_id) == db_ut.get_file_hash(file_id):
            self.update_date_in_file_list(ts)
            self.set_notes_data()

        self.editing = False

    def update_date_in_file_list(self, ts: int):
        if ts > 0:
            a_ts_date = QDateTime()
            a_ts_date.setSecsSinceEpoch(ts)
            ag.file_list.model().update_last_note_data(a_ts_date, ag.file_list.currentIndex())

    @pyqtSlot(fileNote)
    def remove_item(self, note: fileNote):
        file_id = note.get_file_id()
        note_id = note.get_note_id()

        if (self.editing and
            self.editor.get_note_id() == note_id and
            self.editor.get_file_id() == file_id):
            show_message_box(
                'Note is editing now',
                "The note can't be deleted right now.",
                icon=QStyle.StandardPixmap.SP_MessageBoxWarning,
                details="It is editing!"
            )
            return

        def msg_callback(res: int):
            if res == 1:
                self.scroll_layout.removeWidget(note)
                note.deleteLater()
                db_ut.delete_note(file_id, note_id)

        show_message_box(
            'delete file note',
            'confirm deletion of note',
            btn=QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel,
            icon=QStyle.StandardPixmap.SP_MessageBoxQuestion,
            callback=msg_callback
        )

    def collapse_all(self):
        for i in reversed(range(self.scroll_layout.count()-1)):
            item = self.scroll_layout.itemAt(i)
            if item.widget():
                note: fileNote = item.widget()
                note.ensure_collapsed()
