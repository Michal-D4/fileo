from PyQt6.QtCore import Qt, QMimeData, QDataStream, QIODevice, QUrl
from PyQt6.QtGui import QFocusEvent, QDropEvent, QDragEnterEvent, QTextCursor
from PyQt6.QtWidgets import QWidget, QTextEdit, QHBoxLayout

from .file_note import fileNote
from ..core import app_globals as ag, db_ut


class noteEditor(QWidget):
    def __init__(self, parent = None) -> None:
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.note_editor = QTextEdit()
        self.layout.addWidget(self.note_editor)

        self.note: fileNote = None
        self.branch = None

        self.note_editor.setAcceptDrops(False)
        self.setAcceptDrops(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def dragEnterEvent(self, e: QDragEnterEvent) -> None:
        mimedata: QMimeData = e.mimeData()
        if ((mimedata.hasFormat(ag.mimeType.files_in.value)
            and e.source() is ag.app)
            or mimedata.hasFormat(ag.mimeType.files_uri.value)):
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e: QDropEvent) -> None:
        def link_string() -> str:
            ref = url.toString()
            name = 'xxx'
            if url.hasFragment():
                name = url.fragment(QUrl.ComponentFormattingOption.FullyDecoded)
            else:
                html = data.html()
                if (t_end := html.rfind('</a>')) > 0:
                    t_beg = html.rfind('>', 0, t_end)
                    if t_end > t_beg+1:
                        name = html[t_beg+1 : t_end]
            return f'[{name}]({ref})'

        data: QMimeData = e.mimeData()
        t: QTextCursor = self.note_editor.cursorForPosition(e.position().toPoint())
        if data.hasFormat(ag.mimeType.files_uri.value):
            url: QUrl = data.urls()[0]
            if url.scheme() == 'file':
                t.insertText(f'[{url.fileName()}]({url.toString().replace(" ","%20")})')
            elif url.scheme().startswith('http'):
                t.insertText(link_string())
            e.accept()
        elif data.hasFormat(ag.mimeType.files_in.value):
            files_data = data.data(ag.mimeType.files_in.value)
            t.insertText(self.inner_file_link(files_data))
        return super().dropEvent(e)

    def inner_file_link(self, file_data) -> str:
        stream = QDataStream(file_data, QIODevice.OpenModeFlag.ReadOnly)
        _ = stream.readInt()
        _ = stream.readInt()
        _ = stream.readInt()
        id_ = stream.readInt()
        filename = db_ut.get_file_name(id_)
        return f'*[{filename}](fileid:/{id_})*'

    def focusOutEvent(self, e: QFocusEvent):
        if e.lostFocus():
            ag.signals_.user_signal.emit('SaveEditState')
        super().focusOutEvent(e)

    def start_edit(self, note: fileNote):
        self.note = note
        self.note_editor.setPlainText(db_ut.get_note(
            self.get_file_id(), self.get_note_id()
            )
        )

    def set_branch(self, branch):
        self.branch = branch

    def get_file_id(self) -> int:
        return self.note.get_file_id() if self.note else 0

    def get_note_id(self) -> int:
        return self.note.get_note_id() if self.note else 0

    def get_branch(self) -> str:
        return self.branch

    def set_text(self, text: str):
        self.note_editor.setPlainText(text)

    def get_text(self):
        return self.note_editor.toPlainText()

    def get_note(self) -> fileNote:
        return self.note

    def set_note(self, note: fileNote):
        self.note = note
