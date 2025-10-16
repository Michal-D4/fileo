# from loguru import logger

from PyQt6.QtCore import Qt, QMimeData, QDataStream, QIODevice, QUrl, QByteArray
from PyQt6.QtGui import QFocusEvent, QDropEvent, QDragEnterEvent, QTextCursor
from PyQt6.QtWidgets import QTextEdit

from .file_note import fileNote
from ..core import app_globals as ag, db_ut


class noteEditor(QTextEdit):
    def __init__(self, parent = None) -> None:
        super().__init__(parent)
        self.note: fileNote = None
        self.dragged = False

        self.setAcceptDrops(True)

        self.focusOutEvent = self.editor_lost_focus
        self.dragMoveEvent = self.dragEnterEvent

    def insertFromMimeData(self, source: QMimeData):
        if self.dragged:
            self.dragged = False
            return
        if source.hasText():
            self.insertPlainText(source.text())
        else:
            super().insertFromMimeData(source)

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
            html = data.html()
            if (t_end := html.rfind('</a>')) > 0:
                t_beg = html.rfind('>', 0, t_end)
                name = html[t_beg+1 : t_end]
            else:
                name = uri.fileName()
                if uri.hasFragment():
                    name = f'{name}#{uri.fragment(QUrl.ComponentFormattingOption.FullyDecoded)}'
            return f'[{name}]({uri.toString()})'

        def insert_file_id() -> str:
            stream = QDataStream(file_data, QIODevice.OpenModeFlag.ReadOnly)
            _ = stream.readInt()    # pid - always of current app
            _ = stream.readInt()    # source dir_id - not used here
            cnt = stream.readInt()  # number of files
            tt = []
            for _ in range(cnt):
                id_ = stream.readInt()
                filename = db_ut.get_file_name(id_)
                tt.append(f'* *[{filename}](fileid:/{id_})*  \n')
            return ''.join(tt)

        def insert_file_uri() -> str:
            stream = QDataStream(file_data, QIODevice.OpenModeFlag.ReadOnly)
            _ = stream.readInt()    # pid - always of current app
            _ = stream.readInt()    # source dir_id - not used here
            cnt = stream.readInt()  # number of files
            tt = []
            for _ in range(cnt):
                id_ = stream.readInt()
                pp = db_ut.get_file_path(id_)
                url = QUrl.fromLocalFile(pp) if pp else pp
                if url:
                    tt.append(f'* [{url.fileName()}]({url.toString().replace(" ","%20")})  \n')
            return ''.join(tt)

        data: QMimeData = e.mimeData()
        t: QTextCursor = self.cursorForPosition(e.position().toPoint())
        if data.hasFormat(ag.mimeType.files_uri.value):
            uris: QUrl = data.urls()
            uri = uris[0]
            if uri.scheme() == 'file':
                tt = []
                for ur in uris:
                    tt.append(f'* [{ur.fileName()}]({ur.toString().replace(" ","%20")}  )')
                t.insertText('\n'.join(tt))
            elif uri.scheme().startswith('http'):
                t.insertText(link_string())
            e.accept()
        elif data.hasFormat(ag.mimeType.files_in.value):
            file_data: QByteArray = data.data(ag.mimeType.files_in.value)
            t.insertText(
                insert_file_uri()
                if e.modifiers() & (Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.ShiftModifier) else
                insert_file_id()
            )
        self.dragged = True
        return super().dropEvent(e)

    def editor_lost_focus(self, e: QFocusEvent):
        if e.lostFocus():
            ag.signals.user_signal.emit('SaveEditState')
        super().focusOutEvent(e)

    def start_edit(self, note: fileNote):
        self.note = note
        self.setPlainText(db_ut.get_note(self.get_file_id(), self.get_note_id()))

    def get_file_id(self) -> int:
        return self.note.get_file_id() if self.note else 0

    def get_note_id(self) -> int:
        return self.note.get_note_id() if self.note else 0

    def set_text(self, text: str):
        self.setPlainText(text)

    def get_text(self):
        return self.toPlainText()

    def get_note(self) -> fileNote:
        return self.note

    def set_note(self, note: fileNote):
        self.note = note
