from loguru import logger
import os
from pathlib import Path

from PyQt6.QtCore import Qt, QPoint, pyqtSlot
from PyQt6.QtGui import (QMouseEvent, QTextCursor, QAction,
    QKeySequence,
)
from PyQt6.QtWidgets import QTextBrowser, QMenu, QMessageBox

from ..core import app_globals as ag, db_ut, low_bk


class Locations(QTextBrowser):
    def __init__(self, parent = None) -> None:
        super().__init__(parent)
        self.file_id = 0
        self.branches = []
        self.is_all_selected = False
        self.names = {}

        self.cur_pos = QPoint()
        self.setTabChangesFocus(False)

    def mousePressEvent(self, e: QMouseEvent) -> None:
        _keys = ["Copy", "go to this location", "Reveal in explorer",
                      "delete file from this location", "delimiter",
                      "Remove duplicate file", "delimiter", "Select All"]
        _menu = { # key is menu items text, (the_must, method, shortcut)
            _keys[0]: (True, self.copy, QKeySequence.StandardKey.Copy),
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

    def get_branch(self, file_id: int=0) -> list:
        """
        returns the first branch the file belongs to
        """
        if file_id == 0:
            return []
        for branch, f_id in self.names.values():
            if f_id == file_id:
                return branch
        return []

    def go_file(self):
        branch = ','.join((str(i) for i in self.branch[0]))
        ag.signals_.user_signal.emit(
            f'file-note: Go to file\\{self.branch[1]}-{branch}'
        )

    def delete_file(self):
        ag.signals_.user_signal.emit(
            f'remove_file_from_location\\{self.branch[-1]},{self.branch[0][-1]}' # file_id, dir_id
        )

    def set_current_branch(self) -> str:
        line = self.select_line_under_mouse()
        self.branch = self.names.get(line, [])
        return line

    def reveal_file(self):
        ag.signals_.user_signal.emit(f'file reveal\\{self.branch[1]}')

    def remove_duplicate(self):
        def get_other_branch():
            for bb in self.names.values():
                if bb[1] != file_id:
                    return bb
            return ((0,), 0)

        file_id = self.branch[1]
        path = db_ut.get_file_path(file_id)
        res = ag.show_message_box(
            'Removing duplicate file',
            'A file will be deleted to the trash. Please confirm',
            btn=QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel,
            icon=QMessageBox.Icon.Question
        )
        if res == QMessageBox.StandardButton.Ok:
            other_branch, other_fileid = get_other_branch()
            pp = Path(path)
            logger.info(f'{file_id=}, {str(pp)}')
            try:
                os.remove(str(pp))
            except FileNotFoundError:
                pass
            finally:   # delete from DB independent on os.remove result
                logger.info(f'{other_fileid=}, {other_branch}')
                db_ut.delete_file(file_id)
                ag.file_data.set_data(other_fileid, other_branch)

    def select_line_under_mouse(self) -> QTextCursor:
        txt_cursor = self.cursorForPosition(self.cur_pos)
        txt_cursor.select(QTextCursor.SelectionType.LineUnderCursor)
        sel_text = txt_cursor.selectedText().split(' \xa0'*4)[0]  # exclude duplication info, if any
        self.setTextCursor(txt_cursor)
        return sel_text

    def set_data(self, file_id: int):
        self.set_file_id(file_id)
        if ag.mode is ag.appMode.DIR:
            curr_branch = low_bk.define_branch(ag.dir_list.currentIndex())
        else:
            curr_branch = []
        self.show_branches(curr_branch)

    def set_file_id(self, file_id: int):
        self.has_dups = False
        self.file_id = file_id
        self.get_leaves()
        self.build_branches()
        self.build_branch_data()

    def get_leaves(self):
        dirs = self.get_file_dirs()
        self.branches.clear()
        for dd in dirs:
            self.branches.append(
                [(dd.id, dd.file_id), dd.parent_id]
            )

    def get_file_dirs(self) -> list:
        dir_ids = db_ut.get_file_dir_ids(self.file_id)
        dirs = []
        for dir_id, file_id in dir_ids:
            for pp in db_ut.dir_parents(dir_id):
                dirs.append(ag.DirData(*pp, file_id))
        return dirs

    def build_branches(self):
        def add_dir_parent() -> list:
            ss = tt[:-1]
            tt[-1] = (qq.id, )
            tt.append(qq.parent_id)
            return ss

        curr = 0
        while 1:
            if curr >= len(self.branches):
                break
            tt = self.branches[curr]

            while 1:
                if tt[-1] == 0:  # 0 is root dir
                    break
                parents = db_ut.dir_parents(tt[-1])
                first = True
                for pp in parents:
                    qq = ag.DirData(*pp)
                    if first:
                        ss = add_dir_parent()
                        first = False
                        continue
                    self.branches.append(
                        [*ss, (qq.id, ), qq.parent_id]
                    )
            curr += 1

    def show_branches(self, curr_branch: list) -> str:
        self.has_dups = False
        def file_branch_line():
            return (
                f'<ul><li type="circle">{key0}</li></ul>'
                if val[0] == curr_branch and val[1] == self.file_id else
                f'<p><blockquote>{key0}</p>'
            )

        def dup_file_branch_line():
            file_name = db_ut.get_file_name(val[1])
            self.has_dups = True
            return (
                (
                    f'<ul><li type="circle">{key0} &nbsp; &nbsp; '
                    f'&nbsp; &nbsp; ----> &nbsp; Dup: {file_name}</li></ul>'
                )
                if val[0] == curr_branch and val[1] == self.file_id else
                (
                    f'<p><blockquote>{key0} &nbsp; &nbsp; &nbsp; '
                    f'&nbsp; ----> &nbsp; Dup: {file_name}</p>'
                )
            )

        txt = [
            '<HEAD><STYLE type="text/css"> p, li {text-align: left; '
            'text-indent:-28px; line-height: 66%} </STYLE> </HEAD> <BODY> '
        ]
        for key, val in self.names.items():
            key0 = key.split('/')[0]
            tt = (
                file_branch_line()
                if val[1] == self.file_id else
                dup_file_branch_line()
            )
            txt.append(tt)

        txt.append('<p/></BODY>')

        self.setHtml(''.join(txt))

    def build_branch_data(self):
        self.names.clear()
        for bb in self.branches:
            key, val = self.branch_names(bb)
            self.names[key] = val

    def branch_names(self, bb: list) -> str:
        tt = bb[:-1]
        tt.reverse()
        ww = []
        vv = []
        for folder, *_ in tt:
            # logger.info(f'{folder=}, {suffix=}')
            name = db_ut.get_dir_name(folder)
            ww.append(name)
            vv.append(folder)
        ww[-1] = f'{ww[-1]}/{tt[-1][-1]}'
        return ' > '.join(ww), (vv, tt[-1][-1])
