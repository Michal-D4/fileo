from loguru import logger

from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import (
    QMouseEvent, QTextCursor, QAction,
    QKeySequence,
)
from PyQt6.QtWidgets import QTextBrowser, QMenu

from collections import defaultdict

from ..core import app_globals as ag, db_ut


def add_link_hide_str(dd: ag.DirData):
    tt = f'{"L" if dd.is_link else ""}{"H" if dd.hidden else ""}'
    return f'({tt})' if tt else ''   ## () around "L", "H", "LH"

class Locations(QTextBrowser):
    def __init__(self, parent = None) -> None:
        super().__init__(parent)
        self.file_id = 0
        self.branches = []
        self.names = defaultdict(list)

        self.cur_pos = QPoint()
        self.setTabChangesFocus(False)

    def mousePressEvent(self, e: QMouseEvent) -> None:
        _menu_dscr = { # key is menu items text, (obligatory item, method to call, shortcut)
            "Copy": (True, self.copy, QKeySequence.StandardKey.Copy),
            "goto this location": (False, self.go_file, None),
            "Reveal in explorer": (False, self.reveal_file, None),
            "delete file from this location": (False, self.delete_file, None),
            "delimiter": (True, None, None),
            "Select All": (True, self.selectAll, QKeySequence.StandardKey.SelectAll),
        }

        def create_menu() -> QMenu:
            menu = QMenu(self)
            actions = []
            for key, dscr in _menu_dscr.items():
                must, meth, short = dscr
                if must or self.branch:
                    if meth:
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
                _menu_dscr[action.text()][1]()

        def branch_under_mouse():
            line = self.select_line_under_mouse(self.cur_pos)
            return self.names.get(line, [])

        self.cur_pos = e.pos()

        if e.buttons() is Qt.MouseButton.LeftButton:
            self.select_line_under_mouse(self.cur_pos)
        elif e.buttons() is Qt.MouseButton.RightButton:
            self.branch = branch_under_mouse()
            menu = create_menu()
            local_menu()

    def get_branch(self, file_id: int=0) -> list:
        """
        returns the first branch the file belongs to
        """
        branches = list(self.names.values())
        if file_id == 0:
            return []
        for blist in branches:
            for bb in blist:
                if bb[1] == file_id:
                    return bb[0]
        return []

    def go_file(self):
        branch = ','.join((str(i) for i in self.branch[0][0]))
        ag.signals_.user_signal.emit(
            f'file-note: Go to file\\{self.branch[0][1]}-{branch}'
        )

    def delete_file(self):
        ag.signals_.user_signal.emit(
            f'remove_file_from_location\\{self.branch[0][-1]},{self.branch[0][0][-1]}'
        )

    def reveal_file(self):
        ag.signals_.user_signal.emit(f'file reveal\\{self.branch[0][1]}')

    def select_line_under_mouse(self, pos: QPoint) -> QTextCursor:
        txt_cursor = self.cursorForPosition(pos)
        txt_cursor.select(QTextCursor.SelectionType.LineUnderCursor)
        sel_text = txt_cursor.selectedText().split(' \xa0'*4)[0]  # exclude duplication info, if any
        self.setTextCursor(txt_cursor)
        return sel_text

    def set_data(self, file_id: int, curr_branch: list):
        # logger.info(f'{file_id=}, {curr_branch=}')
        self.set_file_id(file_id)
        self.show_branches(curr_branch)

    def set_file_id(self, file_id: int):
        self.file_id = file_id
        self.get_leaves()
        self.build_branches()
        self.build_branch_data()

    def get_leaves(self):
        dirs = self.get_file_dirs()
        self.branches.clear()
        for dd in dirs:
            self.branches.append(
                [(dd.id, add_link_hide_str(dd), dd.file_id), dd.parent_id]
            )

    def get_file_dirs(self) -> list:
        dir_ids = db_ut.get_file_dir_ids(self.file_id)
        dirs = []
        for row in dir_ids:         # row = (dir_id, file_id)
            parents = db_ut.dir_parents(row[0])
            for pp in parents:
                dirs.append(ag.DirData(*pp, row[1]))
        return dirs

    def build_branches(self):
        def add_dir_parent() -> list:
            ss = tt[:-1]
            tt[-1] = (qq.id, add_link_hide_str(qq))
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
                        [*ss, (qq.id, add_link_hide_str(qq)), qq.parent_id]
                    )
            curr += 1

    def show_branches(self, curr_branch: list) -> str:
        def file_branch_line():
            return (
                f'<ul><li type="circle">{key}</li></ul>'
                if vv[0] == curr_branch else
                f'<p><blockquote>{key}</p>'
            )

        def dup_file_branch_line():
            file_name = db_ut.get_file_name(vv[1])
            return (
                (
                    f'<ul><li type="circle">{key} &nbsp; &nbsp; '
                    f'&nbsp; &nbsp; ----> &nbsp; Dup: {file_name}</li></ul>'
                )
                if vv[0] == curr_branch else
                (
                    f'<p><blockquote>{key} &nbsp; &nbsp; &nbsp; '
                    f'&nbsp; ----> &nbsp; Dup: {file_name}</p>'
                )
            )

        txt = [
            '<HEAD><STYLE type="text/css"> p, li {text-align: left; '
            'text-indent:-28px; line-height: 66%} </STYLE> </HEAD> <BODY> '
        ]
        for key, val in self.names.items():
            for vv in val:
                tt = (
                    file_branch_line()
                    if vv[1] == self.file_id else
                    dup_file_branch_line()
                )
                txt.append(tt)

        txt.append('<p/></BODY>')
        self.setHtml(''.join(txt))

    def build_branch_data(self):
        self.names.clear()
        for bb in self.branches:
            key, val = self.branch_names(bb)
            self.names[key].append(val)

    def branch_names(self, bb: list) -> str:
        tt = bb[:-1]
        tt.reverse()
        ww = []
        vv = []
        for node in tt:
            name = db_ut.get_dir_name(node[0])
            ww.append(f'{name}{node[1]}')
            vv.append(node[0])
        return ' > '.join(ww), (vv, tt[-1][-1])
