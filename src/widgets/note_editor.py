from loguru import logger

from PyQt6.QtCore import Qt, QMimeData, QDataStream, QIODevice, QUrl, QByteArray
from PyQt6.QtGui import QFocusEvent, QDropEvent, QDragEnterEvent, QTextCursor
from PyQt6.QtWidgets import QWidget, QTextEdit, QHBoxLayout

from .file_note import fileNote
from ..core import app_globals as ag, db_ut
from .. import tug


class noteEditor(QWidget):
    def __init__(self, parent = None) -> None:
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.note_editor = QTextEdit()
        self.layout.addWidget(self.note_editor)

        self.note: fileNote = None
        self.drag_enter_btns = 0

        self.note_editor.setAcceptDrops(False)
        self.setAcceptDrops(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.note_editor.focusOutEvent = self.editor_lost_focus
        self.note_editor.setStyleSheet(tug.get_dyn_qss("note_edit"))

    def dragEnterEvent(self, e: QDragEnterEvent) -> None:
        mimedata: QMimeData = e.mimeData()
        if ((mimedata.hasFormat(ag.mimeType.files_in.value)
            and e.source() is ag.app)
            or mimedata.hasFormat(ag.mimeType.files_uri.value)):
            # logger.info(f'{e.buttons()=}')
            self.drag_enter_btns = e.buttons()
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
        t: QTextCursor = self.note_editor.cursorForPosition(e.position().toPoint())
        if data.hasFormat(ag.mimeType.files_uri.value):
            uris: QUrl = data.urls()
            uri = uris[0]
            # logger.info(f'{uri.scheme()=}')
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
            logger.info(f'{e.buttons()=}')  # intensionaly, to see if Qt recover bottons in dropEvent
            t.insertText(
                insert_file_id()
                # if e.buttons() & Qt.MouseButton.LeftButton
                if self.drag_enter_btns & Qt.MouseButton.LeftButton
                else insert_file_uri()
            )
        return super().dropEvent(e)

    def editor_lost_focus(self, e: QFocusEvent):
        if e.lostFocus():
            ag.signals_.user_signal.emit('SaveEditState')
        super().focusOutEvent(e)

    def start_edit(self, note: fileNote):
        self.note = note
        self.note_editor.setPlainText(db_ut.get_note(
            self.get_file_id(), self.get_note_id()
            )
        )

    def get_file_id(self) -> int:
        return self.note.get_file_id() if self.note else 0

    def get_note_id(self) -> int:
        return self.note.get_note_id() if self.note else 0

    def set_text(self, text: str):
        self.note_editor.setPlainText(text)

    def get_text(self):
        return self.note_editor.toPlainText()

    def get_note(self) -> fileNote:
        return self.note

    def set_note(self, note: fileNote):
        self.note = note
