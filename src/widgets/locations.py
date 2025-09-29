# from loguru import logger
import os
from pathlib import Path

from PyQt6.QtCore import Qt, QPoint, pyqtSlot
from PyQt6.QtGui import (QMouseEvent, QTextCursor, QAction,
    QKeySequence,
)
from PyQt6.QtWidgets import QTextBrowser, QMenu, QMessageBox, QStyle

from ..core import app_globals as ag, db_ut


class Locations(QTextBrowser):
    def __init__(self, parent = None) -> None:
        super().__init__(parent)
        self.file_id = 0
        self.branches = []
        self.is_all_selected = False
        self.names = {}

        self.cur_pos = QPoint()

    def mousePressEvent(self, e: QMouseEvent) -> None:
        _keys = ["Copy", "go to this location", "Reveal in explorer",
                      "delete file from this location", "delimiter",
                      "Remove duplicate file", "delimiter", "Select All"]
        _menu = { # key is menu items text, (the_must, method, shortcut)
            _keys[0]: (False, self.copy, QKeySequence.StandardKey.Copy),
            _keys[1]: (False, self.go_file, None),
            _keys[2]: (False, self.reveal_file, None),
            _keys[3]: (False, self.delete_file, None),
            _keys[4]: (True, None, None),
            _keys[5]: (False, self.remove_duplicate, None),
            _keys[7]: (True, self.selectAll, QKeySequence.StandardKey.SelectAll),
        }

        def create_menu() -> QMenu:
            menu = QMenu(self)
            actions = []
            for key in _keys:
                must, meth, short = _menu[key]
                if must or line:
                    if key == "Remove duplicate file":
                        if self.has_dups:
                            actions.append(QAction(key, self))
                    elif meth:
                        actions.append(QAction(key, self))
                        if short:
                            actions[-1].setShortcut(short)
                    else:
                        actions.append(QAction(self))
                        actions[-1].setSeparator(True)
            menu.addActions(actions)
            return menu

        def local_menu():
            action = menu.exec(self.mapToGlobal(self.cur_pos))
            if action:
                self.setUpdatesEnabled(False)
                _menu[action.text()][1]()
                if self.is_all_selected:
                    self.selectAll()
                self.setUpdatesEnabled(True)

        self.cur_pos = e.pos()

        line = self.set_current_branch()
        if e.buttons() is Qt.MouseButton.LeftButton:
            self.is_all_selected = False
        elif e.buttons() is Qt.MouseButton.RightButton:
            menu = create_menu()
            local_menu()

    @pyqtSlot()
    def selectAll(self):
        super().selectAll()
        self.is_all_selected = True

    @pyqtSlot()
    def copy(self):
        if self.is_all_selected:
            self.selectAll()
        super().copy()

    def go_file(self):
        branch = ','.join((str(i) for i in self.branch[0]))
        file_id = self.branch[1]
        ag.signals_.user_signal.emit(f'file-note: Go to file\\{file_id}-{branch}')

    def delete_file(self):
        branch, file_id = self.branch
        ag.signals_.user_signal.emit(f'remove_file_from_location\\{file_id},{branch[-1]}')

    def set_current_branch(self) -> str:
        line = self.select_line_under_mouse()
        self.branch = self.names.get(line, [])
        return line

    def reveal_file(self):
        ag.signals_.user_signal.emit(f'file reveal\\{self.branch[1]}')

    def remove_duplicate(self):
        def get_other_branch() -> int:
            for bb in self.names.values():
                if bb[1] != file_id:
                    return bb[1]
            return 0

        def msg_callback(res: int):
            if res == 1:
                other_fileid = get_other_branch()
                # logger.info(f'{file_id=}, {path}')
                try:
                    os.remove(str(Path(path)))  # in DB path saved in posix format, str(Path) -> native to os
                except FileNotFoundError:
                    pass
                finally:   # delete from DB independent on os.remove result
                    # logger.info(f'{file_id=} - {other_fileid=}')
                    db_ut.delete_file(file_id)
                    ag.file_data.set_data(other_fileid)

        file_id = self.branch[1]
        path = db_ut.get_file_path(file_id)
        ag.show_message_box(
            'Removing duplicate file',
            'A file will be deleted to the trash. Please confirm',
            btn=QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel,
            icon=QStyle.StandardPixmap.SP_MessageBoxQuestion,
            callback=msg_callback
        )

    def select_line_under_mouse(self) -> QTextCursor:
        txt_cursor = self.cursorForPosition(self.cur_pos)
        txt_cursor.select(QTextCursor.SelectionType.LineUnderCursor)
        sel_text = txt_cursor.selectedText()
        self.setTextCursor(txt_cursor)
        return sel_text.replace('\xa0', ' ')

    def set_data(self, file_id: int):
        self.set_file_id(file_id)
        if ag.mode is ag.appMode.DIR:
            *curr_branch, _ = ag.define_branch(ag.dir_list.currentIndex())
        else:
            curr_branch = []
        self.show_branches(curr_branch)

    def set_file_id(self, file_id: int):
        self.has_dups = False
        self.file_id = file_id
        self.build_branches()
        self.build_branch_data()

    def build_branches(self):
        def get_leaves():
            for file_id, dir_id in db_ut.get_file_dir_ids(self.file_id):
                leaves.append([file_id, dir_id])
            return leaves

        self.branches.clear()
        leaves = []
        get_leaves()
        curr = 0
        while curr < len(leaves):   # not for-loop because len(leaves) changed in loop
            tt = leaves[curr]
            for parent, *_ in db_ut.dir_parents(tt[-1]):
                if not parent:
                    self.branches.append(tt)
                    continue
                leaves.append([*tt, parent])
            curr += 1

    def show_branches(self, curr_branch: list) -> str:
        self.has_dups = False
        def file_branch_line():
            return (
                (f'<ul><li type="circle">{key0}</li></ul>', key0)
                if val[0] == curr_branch and val[1] == self.file_id else
                (f'<p><blockquote>{key0}</p>', key0)
            )

        def dup_file_branch_line():
            file_name = db_ut.get_file_name(val[1])
            ku_key = f'{key0} &nbsp; &nbsp; &nbsp; &nbsp; ----> &nbsp; Dup: {file_name}'
            nu_key = f'{key0}         ---->   Dup: {file_name}'
            self.has_dups = True
            return f'<p><blockquote>{ku_key}</p>', nu_key

        re_names = {}
        txt = [
            '<HEAD><STYLE type="text/css"> p, li {text-align: left; '
            'text-indent:-28px; line-height: 66%} </STYLE> </HEAD> <BODY> '
        ]
        for key, val in self.names.items():
            key0, *_ = key.split('/')
            tt, nu_key = (
                file_branch_line() if val[1] == self.file_id else dup_file_branch_line()
            )
            re_names[nu_key] = val
            txt.append(tt)

        self.names = re_names
        txt.append('<p/></BODY>')
        self.setHtml(''.join(txt))

    def build_branch_data(self):
        self.names.clear()
        for file_id, *bb in self.branches:
            key, val = self.branch_names(file_id, bb)
            self.names[key] = val

    def branch_names(self, file_id: int, bb: list) -> tuple:
        tt = bb
        tt.reverse()
        ww = []
        for folder in tt:
            name = db_ut.get_dir_name(folder)
            ww.append(name)
        ww[-1] = f'{ww[-1]}/{file_id}'
        return ' > '.join(ww), (tt, file_id)
