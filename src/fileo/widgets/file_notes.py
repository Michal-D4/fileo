from loguru import logger

from PyQt6.QtCore import Qt, QUrl, QDateTime, QPoint
from PyQt6.QtGui import QGuiApplication, QResizeEvent, QMouseEvent
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
    QFrame, QSpacerItem, QSizePolicy, QToolButton, QTextEdit,
    QMessageBox, QTextBrowser, QStackedWidget
)

from datetime import datetime

from .ui_notes import Ui_FileNotes

from core import icons, app_globals as ag, db_ut
from core.compact_list import aBrowser
from widgets.file_info import fileInfo

time_format = "%Y-%m-%d %H:%M"

class noteEditor(QWidget):
    def __init__(self, fileid: int, id=0, parent = None) -> None:
        super().__init__(parent)
        self.id = id
        self.file_id = fileid

        self.set_layout()

        self.Ok.setIcon(icons.get_other_icon("ok"))
        self.Ok.clicked.connect(self.save_note)
        self.Cancel.setIcon(icons.get_other_icon("cancel2"))
        self.Cancel.clicked.connect(self.cancel)

    def save_note(self):
        ag.signals_.file_note_changed.emit(
            self.id, self.editor.toPlainText()
        )
        self.close()

    def set_text(self, data: str):
        self.editor.setText(data)

    def cancel(self):
        self.close()

    def set_layout(self):
        vLayout2 = QVBoxLayout(self)
        vLayout2.setContentsMargins(0, 0, 0, 0)
        vLayout2.setSpacing(0)

        frame = QFrame(self)
        frame.setFrameShape(QFrame.Shape.Box)
        frame.setFrameShadow(QFrame.Shadow.Raised)

        vLayout = QVBoxLayout(frame)
        vLayout.setContentsMargins(0, 0, 0, 0)
        vLayout.setSpacing(0)

        hLayout = QHBoxLayout()
        hLayout.setContentsMargins(9, -1, 9, -1)

        spacerItem = QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Minimum)
        hLayout.addItem(spacerItem)

        self.Ok = QToolButton(frame)
        self.Ok.setObjectName("Ok")
        hLayout.addWidget(self.Ok)

        self.Cancel = QToolButton(frame)
        self.Cancel.setObjectName("Cancel")
        hLayout.addWidget(self.Cancel)

        vLayout.addLayout(hLayout)
        self.editor = QTextEdit(frame)
        self.editor.setFrameShape(QFrame.Shape.NoFrame)
        self.editor.setObjectName("editor")
        vLayout.addWidget(self.editor)
        vLayout2.addWidget(frame)

        ss = ag.dyn_qss['tag_list_border'][0]
        tt = ag.dyn_qss['note_editor'][0]
        self.setStyleSheet(' '.join((ss, tt)))


class tagBrowser(aBrowser):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

    def show_in_bpowser(self):
        style = ag.dyn_qss['text_browser'][0]
        self.browser.clear()

        txt = ''.join((style, self.html_selected()))

        self.browser.setText(txt)

    def html_selected(self):
        sel = self.selected_idx
        inn = ' '.join(f"<a class={'s' if i in sel else 't'} href=#{tag}>{tag}</a> "
             for i,tag in enumerate(self.tags))

        clo = ('<p><a><style type="text/css">*[href]{text-decoration: none; '
            'color: red}</style></a><span class="fa">'
            '<a class=t href=lnk--1>&#xf410;</a></span></p>')

        txt = (f'<table width="100%"><tr><td width="95%">{inn}</td>'
            f'<td align="right">{clo}</td></tr></table>')
        return txt


class notesBrowser(QWidget, Ui_FileNotes):
    def __init__(self, parent = None) -> None:
        super().__init__(parent)
        self.tags = []
        self.tag_id = []
        self.selected = []
        self.file_id = 0
        self.id = 0

        self.setupUi(self)

        ag.signals_.file_note_changed.connect(self.note_changed)
        self.tagEdit.mouseDoubleClickEvent = self.pick_tags
        self.tagEdit.editingFinished.connect(self.tag_list_changed)

        self.set_stack_pages()

        self.plus.setIcon(icons.get_other_icon("plus"))
        self.plus.clicked.connect(self.new_comment)
        self.browser.anchorClicked.connect(self.ref_clicked)

        self.selectors = [
            self.l_tags, self.l_autotrs,
            self.l_locations, self.l_file_info,
            self.l_comments
        ]
        self.switch_page(4)

        self.l_tags.mousePressEvent = self.l_tags_press
        self.l_autotrs.mousePressEvent = self.l_autotrs_press
        self.l_locations.mousePressEvent = self.l_locations_press
        self.l_file_info.mousePressEvent = self.l_file_info_press
        self.l_comments.mousePressEvent = self.l_comments_press

    def set_stack_pages(self):
        self.stackedWidget = QStackedWidget(self)
        self.stackedWidget.setObjectName("stackedWidget")

        # add tag selector page (0)
        self.tag_selector = tagBrowser(self)
        self.stackedWidget.addWidget(self.tag_selector)
        # self.tag_selector - set data

        # add author selector page (1)
        self.author_selector = tagBrowser()
        self.stackedWidget.addWidget(self.author_selector)
        # self.author_selector - set data

        # add file locations page (2)
        self.locator = QTextBrowser(self)
        self.stackedWidget.addWidget(self.locator)

        # add file info page (3)
        self.file_info = fileInfo(self)
        self.stackedWidget.addWidget(self.file_info)

        # add comments page (4)
        self.browser = QTextBrowser(self)
        self.stackedWidget.addWidget(self.browser)
        self.browser.setOpenLinks(False)

        # add comment editor page (5)
        self.editor = noteEditor(0, 0)
        self.stackedWidget.addWidget(self.editor)

        self.verticalLayout.addWidget(self.stackedWidget)
        self.setStyleSheet(ag.dyn_qss['note_frames'][0])

    def l_tags_press(self, e: QMouseEvent):
        self.switch_page(0)

    def l_autotrs_press(self, e: QMouseEvent):
        self.switch_page(1)

    def l_locations_press(self, e: QMouseEvent):
        self.switch_page(2)

    def l_file_info_press(self, e: QMouseEvent):
        self.switch_page(3)

    def l_comments_press(self, e: QMouseEvent):
        self.switch_page(4)

    def switch_page(self, page_no: int):
        logger.info(f'{page_no=}')
        self.cur_page = page_no
        self.title.setText('Authors:' if page_no == 1 else 'Tags:')

        for i, lbl in enumerate(self.selectors):
            if i == page_no:
                lbl.setStyleSheet(
                    'border-left: none;'
                    'border-top: none;'
                    'border-right: none;'
                    'border-bottom: 1px solid #000;'
                )
                continue
            lbl.setStyleSheet('border: none;')
        self.stackedWidget.setCurrentIndex(page_no)

    def note_changed(self, id: int, txt: str):
        if id:
            ts = db_ut.update_note(self.file_id, id, txt)
        else:
            ts = db_ut.insert_note(self.file_id, txt)

        if ts > 0:
            a = QDateTime()
            a.setSecsSinceEpoch(ts)
            ag.file_list.model().update_field_by_name(
                a, "Commented", ag.file_list.currentIndex()
            )
            self.set_notes_data(db_ut.get_file_notes(self.file_id))

    def tag_list_changed(self):
        old = [  # list of selected tags before start editing
            self.tags[self.tag_id.index(i)] for i in self.selected
        ]
        new = self.new_tag_list()

        self.remove_tags(old, new)
        if self.add_tags(old, new):
            ag.signals_.user_action_signal.emit("tag_inserted")

    def new_tag_list(self):
        """
        tag can't contain blanks and can't be empty string
        """
        tmp = self.tagEdit.text().replace(' ','')
        return [t for t in tmp.split(',') if t]

    def add_tags(self, old, new) -> bool:
        ret = False
        diff = set(new) - set(old)
        for d in diff:   # only new in diff
            if d in self.tags:
                id = self.tag_id[self.tags.index(d)]
            else:
                id = db_ut.insert_tag(d)
                self.tag_id.append(id)
                self.tags.append(d)
                ret = True
            self.selected.append(id)
            db_ut.insert_tag_file(id, self.file_id)
        return ret

    def remove_tags(self, old, new):
        """
        remove tag ids from self.selected list
        """
        diff = set(old) - set(new)
        for d in diff:   # only old in diff
            id = self.tag_id[self.tags.index(d)]
            self.selected.remove(id)

    def section_title(self, id: int, mod: str, cre: str) -> str:
        btn1 = f'<span class="fa"><a class=t href=x,lnk{id}>&#xf00d;</a></span>'
        btn2 = f'<span class="fa"><a class=t href=,,lnk{id}>&#xf044;</a></span>'
        hdr = ('<style>td{text-align: center;} '
            '*[href]{text-decoration: none; color: gray} '
            'table{background-color:#FFFFE0;}</style>'
            f'<table width="98%"><tr><td width="45%">modified: {mod}</td>'
            f'<td width="45%">created: {cre}</td>'
            f'<td align="right">{btn1}</td>'
            f'<td align="right">{btn2}</td></tr></table>'
        )
        return hdr

    def set_notes_data(self, data):
        buf = []
        for row in data:
            note = ag.Note(*row)
            head = self.section_title(
                note.id,
                note.modified.strftime(time_format),
                note.created.strftime(time_format)
            )
            buf.append('\n'.join((head, note.note)))
        self.browser.setMarkdown('\n'.join(buf))

    def new_comment(self):
        self.start_edit(0)

    def ref_clicked(self, href: QUrl):
        tref = href.toString()
        if tref.startswith("x,lnk"):
            if self.confirm_deletion():
                id = int(tref[5:])
                self.delete_note(id)
            return
        if tref.startswith(",,lnk"):
            id = int(tref[5:])
            self.start_edit(id)
            return
        if tref.startswith('http'):
            # TODO open link in default browser
            return
        self.set_selection(tref)

    def confirm_deletion(self):
        dlg = QMessageBox(ag.app)
        dlg.setWindowTitle('delete file note')
        dlg.setText(f'confirm deletion of note')
        dlg.setStandardButtons(QMessageBox.StandardButton.Ok |
            QMessageBox.StandardButton.Cancel)
        dlg.setIcon(QMessageBox.Icon.Question)
        return dlg.exec() == QMessageBox.StandardButton.Ok

    def delete_note(self, id: int):
        if id:
            db_ut.delete_note(self.file_id, id)
            self.set_notes_data(db_ut.get_file_notes(self.file_id))

    def start_edit(self, id: int):
        txt = ''
        if id:
            txt = db_ut.get_note(self.file_id, id)
        self.edit_note(id, txt)

    def set_selection(self, ref: str):
        mod = QGuiApplication.keyboardModifiers()
        i = self.tags.index(ref)
        if mod is Qt.KeyboardModifier.ControlModifier:
            if i in self.selected:
                self.selected.remove(i)
            else:
                self.selected.append(i)
        else:
            self.selected.clear()
            self.selected.append(i)

    def set_tags(self, tags):
        """
        tags: list of tags from DB: (tag, id) pairs
        """
        self.tags.clear()
        self.tag_id.clear()
        for it in tags:
            self.tags.append(it[0])
            self.tag_id.append(it[1])

    def set_file_id(self, id: int):
        self.file_id = id
        self.set_selected()

    def set_selected(self):
        file_tag_ids = db_ut.get_file_tagid(self.file_id)
        self.selected = [int(s[0]) for s in file_tag_ids]
        tt = [
            tag for i,tag in enumerate(self.tags)
            if self.tag_id[i] in self.selected]
        self.tagEdit.setText(', '.join(tt))

    def update_tags(self, tags: list[str]):
        self.tagEdit.setText(', '.join(tags))
        self.tag_list_changed()

    def get_selected_tag_ids(self):
        pp = self.tagEdit.text()
        if pp:
            tt = [tag.strip() for tag in pp.split(',')]
            return [self.tag_id[self.tags.index(tag)] for tag in tt]
        return []

    def pick_tags(self, event):
        self.tag_selector = tagBrowser()
        self.tag_selector.change_selection.connect(self.update_tags)
        self.tag_selector.setParent(self)
        self.tag_selector.setObjectName("tag_editor")
        self.tag_selector.setContentsMargins(5,5,5,5)
        ss = ag.dyn_qss['tag_list_border'][0]
        self.tag_selector.setStyleSheet(ss)
        self.tag_selector.move(40, 22)
        self.tag_selector.resize(self.width()-70, max(self.height() // 3, 90))
        self.tag_selector.setMinimumHeight(90)
        self.tag_selector.set_list(zip(self.tags, self.tag_id))
        self.tag_selector.set_selection(self.selected)
        self.tag_selector.show()

    def edit_note(self, id: int, txt: str):
        self.editor = noteEditor(self.file_id, id)
        self.editor.setParent(self)
        self.editor.setObjectName("tag_editor")
        self.editor.setContentsMargins(5,5,5,5)
        self.editor.move(40, 22)
        self.editor.resize(self.width()-70, self.height()-40)
        self.editor.set_text(txt)

        self.editor.show()

    def editor_visible(self) -> bool:
        return self.editor.isVisible() if self.editor else False

    def tag_selector_visible(self) -> bool:
        return self.tag_selector.isVisible() if self.tag_selector else False

    def file_info_visible(self) -> bool:
        return self.file_info.isVisible() if self.file_info else False
