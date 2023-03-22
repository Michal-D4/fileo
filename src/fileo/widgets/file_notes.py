from loguru import logger
from collections import defaultdict

from PyQt6.QtCore import Qt, QUrl, QDateTime, QSize, pyqtSlot
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtWidgets import (QWidget, QTextEdit, QSizePolicy,
    QMessageBox, QTextBrowser, QStackedWidget, QPlainTextEdit,
    QVBoxLayout, QHBoxLayout, QToolButton, QFrame,
)

from .ui_notes import Ui_FileNotes

from core import icons, app_globals as ag, db_ut
from core.compact_list import aBrowser
from widgets.file_info import fileInfo

time_format = "%Y-%m-%d %H:%M"

class noteEditor(QTextEdit):
    def __init__(self, parent = None) -> None:
        super().__init__(parent)
        self.id = 0

    def set_note_id(self, id: int):
        self.id = id

    def get_note_id(self) -> int:
        return self.id


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
        return inn


class authorBrowser(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.file_id = 0

        self.setup_ui()

        ag.author_list.edit_finished.connect(self.refresh_data)
        self.br.change_selection.connect(self.update_selection)

    def setup_ui(self):
        self.edit_authors = QPlainTextEdit()
        self.edit_authors.setObjectName('edit_authors')
        self.edit_authors.setMaximumSize(QSize(16777215, 42))
        si_policy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.edit_authors.setSizePolicy(si_policy)
        self.edit_authors.setToolTip(
            'Enter authors separated by commas, '
            'or select in the list below'
            ', use Ctrl+Click to select multiple items'
        )

        self.accept = QToolButton()
        self.accept.setIcon(icons.get_other_icon("ok"))
        self.accept.clicked.connect(self.finish_edit_list)
        self.accept.setToolTip('Accept editing')

        self.reject = QToolButton()
        self.reject.setIcon(icons.get_other_icon("cancel2"))
        self.reject.clicked.connect(self.set_selected_text)
        self.reject.setToolTip('Reject editing')

        v_layout = QVBoxLayout()
        v_layout.setContentsMargins(0, 0, 0, 0)
        v_layout.setSpacing(0)
        v_layout.addWidget(self.accept)
        v_layout.addWidget(self.reject)

        h_layout = QHBoxLayout()
        h_layout.setContentsMargins(0, 0, 0, 0)
        h_layout.setSpacing(0)
        h_layout.addWidget(self.edit_authors)
        h_layout.addLayout(v_layout)

        self.br = aBrowser(brackets=True)
        self.br.setObjectName('author_selector')

        authors = QFrame(self)
        authors.setObjectName('authors')
        f_layout = QVBoxLayout(self)
        f_layout.setContentsMargins(0, 0, 0, 0)

        m_layout = QVBoxLayout(authors)
        m_layout.setContentsMargins(0, 0, 0, 0)
        m_layout.setSpacing(0)
        m_layout.addLayout(h_layout)
        m_layout.addWidget(self.br)

        f_layout.addWidget(authors)

    def refresh_data(self):
        self.set_authors()
        self.set_selected_text()

    def set_authors(self):
        logger.info('<<< ========== >>>')
        self.br.set_list(db_ut.get_authors())

    def set_file_id(self, id: int):
        self.file_id = id
        logger.info(f'>>> {self.file_id=}')
        self.br.set_selection(
            (int(s[0]) for s in db_ut.get_file_author_id(id))
        )
        self.set_selected_text()

    @pyqtSlot()
    def set_selected_text(self):
        self.edit_authors.setPlainText(', '.join(
            (f'[{it}]' for it in self.br.get_selected())
        ))

    @pyqtSlot()
    def finish_edit_list(self):
        old = self.br.get_selected()
        new = self.get_edited_list()
        logger.info(f"{old=}, {new=}")
        self.sel_list_changed(old, new)

    @pyqtSlot(list)
    def update_selection(self, items: list[str]):
        logger.info(f"{items=}")
        self.sel_list_changed(self.get_edited_list(), items)
        txt = (f'[{it}]' for it in items)
        self.edit_authors.setPlainText(', '.join(txt))

    def get_edited_list(self) -> list[str]:
        tt = self.edit_authors.toPlainText()
        tt = tt.replace('[', '')
        tt = tt.replace(']', '')
        return [t.strip() for t in tt.split(',') if t.strip()]

    def sel_list_changed(self, old: list[str], new: list[str]):
        logger.info(f"{old=}, {new=}")
        self.remove_items(old, new)
        self.add_items(old, new)

    def remove_items(self, old: list[str], new: list[str]):
        diff = set(old) - set(new)
        logger.info(f'{diff=}')
        for d in diff:
            if id := self.br.get_tag_id(d):
                logger.info(f'{id=}')
                db_ut.break_file_authors_link(self.file_id, id)
            logger.info(f'{id=}')

    def add_items(self, old: list[str], new: list[str]):
        inserted = False
        diff = set(new) - set(old)
        logger.info(f'{diff=}')
        for d in diff:
            if db_ut.add_author(self.file_id, d):
                inserted = True
        if inserted:
            self.update_list()
            ag.signals_.user_action_signal.emit("author_inserted")

    def update_list(self):
        self.set_authors()
        self.set_file_id(self.file_id)


class Locations(QTextBrowser):
    def __init__(self, parent = None) -> None:
        super().__init__(parent)
        self.file_id = 0

    def set_file_id(self, id: int):
        self.file_id = id
        self.get_locations()

    def get_locations(self):
        branches = defaultdict(list)
        dir_ids = db_ut.get_file_dir_ids(self.file_id)
        dirs = self.get_file_dirs(dir_ids)
        for dir_data in dirs:
            id = dir_data.id
            p_id = dir_data.parent_id
            branches[(id, p_id)].append([id, p_id])
            logger.info(f'{dir_data}')
            logger.info(f'{branches[(id, p_id)]=}')
            self.get_branches(branches[(id, p_id)])

        self.show_branches(branches, dirs)

    def get_file_dirs(self, dir_ids) -> list:
        dirs = []
        for id in dir_ids:
            parents = db_ut.dir_parents(id[0])
            for pp in parents:
                logger.info(f'{id=}, {pp=}')
                dirs.append(ag.DirData(*pp))
        return dirs

    def get_branches(self, bundle: list):
        curr = 0
        while 1:
            tt = bundle[curr]
            while 1:
                if tt[-1] == 0:
                    break
                parents = db_ut.dir_parents(tt[-1])
                first = True
                for pp in parents:
                    if first:
                        ss = [*tt]
                        tt.append(pp[0])
                        first = False
                        continue
                    bundle.append([*ss, pp[0]])
            curr += 1
            if curr >= len(bundle):
                break
        logger.info(f'{bundle=}')

    def show_branches(self, branches: dict[list], dirs: list):
        names = []
        attribs = []
        for dd in dirs:
            dd: ag.DirData
            for bb in branches[(dd.id, dd.parent_id)]:
               attribs.append((dd.is_copy, dd.hidden))
               names.append(self.exec_branch(bb[:-1]))
               logger.info(f'{names[-1]}, {attribs[-1]}')

    def exec_branch(self, ids: list) -> str:
        ids.reverse()
        ww = []
        for id in ids:
            ww.append(db_ut.get_dir_name(id))
        return ' > '.join(ww)


class notesBrowser(QWidget, Ui_FileNotes):
    def __init__(self, parent = None) -> None:
        super().__init__(parent)
        self.file_id = 0
        self.id = 0
        self.maximized = False
        self.s_height = 0

        self.setupUi(self)

        self.page_selectors = [
            self.l_tags, self.l_authors,
            self.l_locations, self.l_file_info,
            self.l_comments
        ]
        self.set_stack_pages()

        self.expand.setIcon(icons.get_other_icon('up'))
        self.expand.clicked.connect(self.up_down)

        self.plus.setIcon(icons.get_other_icon("plus"))
        self.plus.clicked.connect(self.new_comment)

        self.save.setIcon(icons.get_other_icon("ok"))
        self.save.clicked.connect(self.note_changed)

        self.cancel.setIcon(icons.get_other_icon("cancel2"))
        self.cancel.clicked.connect(self.cancel_note_editing)

        self.edit_btns.hide()
        self.plus.hide()
        self.tagEdit.editingFinished.connect(self.finish_edit_tag)

        self.browser.anchorClicked.connect(self.ref_clicked)

        self.cur_page = 0
        self.l_comments_press(None)

        self.l_tags.mousePressEvent = self.l_tags_press
        self.l_authors.mousePressEvent = self.l_authors_press
        self.l_locations.mousePressEvent = self.l_locations_press
        self.l_file_info.mousePressEvent = self.l_file_info_press
        self.l_comments.mousePressEvent = self.l_comments_press

    def set_stack_pages(self):
        self.stackedWidget = QStackedWidget(self)
        self.stackedWidget.setObjectName("stackedWidget")

        # add tag selector page (0)
        self.tag_selector = tagBrowser(self)
        self.stackedWidget.addWidget(self.tag_selector)
        self.tag_selector.setObjectName('tag_selector')
        self.tag_selector.change_selection.connect(self.update_tags)
        ag.tag_list.edit_finished.connect(self.update_tag_list)

        # add author selector page (1)
        self.author_selector = authorBrowser()
        self.stackedWidget.addWidget(self.author_selector)
        self.author_selector.setObjectName('author_selector')

        # add file locations page (2)
        self.locator = Locations(self)
        self.stackedWidget.addWidget(self.locator)
        self.locator.setObjectName('locator')

        # add file info page (3)
        logger.info('before self.file_info = fileInfo(self)')
        self.file_info = fileInfo(self)
        self.stackedWidget.addWidget(self.file_info)

        # add comments page (4)
        self.browser = QTextBrowser(self)
        self.stackedWidget.addWidget(self.browser)
        self.browser.setOpenLinks(False)
        self.browser.setObjectName('notes_browser')

        # add comment editor page (5)
        self.editor = noteEditor()
        self.stackedWidget.addWidget(self.editor)
        self.editor.setObjectName('note_editor')

        ss = ag.dyn_qss['passive_selector'][0]
        for lbl in self.page_selectors:
            lbl.setStyleSheet(ss)

        self.verticalLayout.addWidget(self.stackedWidget)
        self.setStyleSheet(' '.join(ag.dyn_qss['noteFrames']))

    def l_tags_press(self, e: QMouseEvent):
        # tag selector page
        self.switch_page(0)
        self.plus.hide()

    def l_authors_press(self, e: QMouseEvent):
        # author selector page
        self.switch_page(1)
        self.plus.hide()

    def l_locations_press(self, e: QMouseEvent):
        # file locations page
        self.switch_page(2)
        self.plus.hide()

    def l_file_info_press(self, e: QMouseEvent):
        # file info page
        self.switch_page(3)
        self.plus.hide()

    def l_comments_press(self, e: QMouseEvent):
        # comments page
        self.switch_page(4)
        self.plus.show()

    def switch_page(self, page_no: int):
        logger.info(f'{page_no=}, {self.cur_page=}')
        if page_no < 5 and self.cur_page < 5:
            self.page_selectors[self.cur_page].setStyleSheet(
                ag.dyn_qss['passive_selector'][0]
            )
            self.page_selectors[page_no].setStyleSheet(
                ag.dyn_qss['active_selector'][0]
            )
        if self.cur_page == 5 and page_no != 5:
            self.edit_btns.hide()
        self.cur_page = page_no
        self.stackedWidget.setCurrentIndex(page_no)

    def up_down(self):
        if self.maximized:
            self.expand.setIcon(icons.get_other_icon('up'))
            ag.app.ui.noteHolder.setMinimumHeight(self.s_height)
            ag.app.ui.noteHolder.setMaximumHeight(self.s_height)
            ag.file_list.show()
        else:
            self.s_height = self.height()
            self.expand.setIcon(icons.get_other_icon('down'))
            hh = ag.file_list.height() + self.s_height
            ag.app.ui.noteHolder.setMinimumHeight(hh)
            ag.app.ui.noteHolder.setMaximumHeight(hh)
            ag.file_list.hide()
        self.maximized = not self.maximized

    def cancel_note_editing(self):
        self.l_comments_press(None)

    def note_changed(self):
        id = self.editor.get_note_id()
        txt = self.editor.toPlainText()
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
        self.l_comments_press(None)

    def set_data(self):
        self.tag_selector.set_list(db_ut.get_tags())
        self.author_selector.set_authors()

    @pyqtSlot()
    def update_tag_list(self):
        self.tag_selector.set_list(db_ut.get_tags())
        self.set_file_id(self.file_id)

    @pyqtSlot()
    def finish_edit_tag(self):
        old = self.tag_selector.get_selected()
        new = self.new_tag_list()
        logger.info(f'<<< finish edit tags >>>')
        self.tag_list_changed(old, new)

    def tag_list_changed(self, old: list[str], new: list[str]):
        logger.info(f'{old=}, {new=}')
        self.remove_tags(old, new)
        if self.add_tags(old, new):
            self.update_tag_list()
            ag.signals_.user_action_signal.emit("tag_inserted")

    def new_tag_list(self):
        """
        tag can't contain blanks and can't be empty string
        """
        tmp = self.tagEdit.text().replace(' ','')
        return [t for t in tmp.split(',') if t]

    def remove_tags(self, old: list[str], new: list[str]):
        diff = set(old) - set(new)
        for d in diff:
            id = self.tag_selector.get_tag_id(d)
            logger.info(f'{d=}, {id=}, {self.file_id=}')
            db_ut.delete_tag_file(id, self.file_id)

    def add_tags(self, old, new) -> bool:
        inserted = False
        diff = set(new) - set(old)
        for d in diff:
            if not (id := self.tag_selector.get_tag_id(d)):
                id = db_ut.insert_tag(d)
                logger.info(f'inserted; {d=}, {id=}')
                inserted = True
            logger.info(f'{id=}, {self.file_id=}')
            db_ut.insert_tag_file(id, self.file_id)
        return inserted

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
        logger.info(f'{tref=}')
        if tref.startswith("x,lnk"):
            if self.confirm_note_deletion():
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

    def confirm_note_deletion(self):
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
        txt = db_ut.get_note(self.file_id, id) if id else ''
        logger.info(f'{id=}, {txt=}')
        self.editor.setText(txt)
        self.editor.set_note_id(id)
        self.plus.hide()
        self.edit_btns.show()
        self.switch_page(5)

    def set_file_id(self, id: int):
        self.file_id = id
        logger.info(f'{self.file_id=}')
        self.tag_selector.set_selection(
            (int(s[0]) for s in db_ut.get_file_tagid(self.file_id))
        )
        self.tagEdit.setText(', '.join(
            self.tag_selector.get_selected()
            )
        )
        self.file_info.set_file_id(id)
        self.author_selector.set_file_id(id)
        self.locator.set_file_id(id)

    @pyqtSlot(list)
    def update_tags(self, tags: list[str]):
        logger.info(f'{tags=}, {self.tagEdit.text()=}')
        self.tag_list_changed(self.new_tag_list(), tags)
        self.tagEdit.setText(', '.join(tags))
