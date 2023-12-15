from loguru import logger

from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import (
    QMouseEvent, QTextCursor, QAction,
    QKeySequence,
)
from PyQt6.QtWidgets import QTextBrowser, QMenu

from collections import defaultdict

from ..core import icons, app_globals as ag, db_ut

MENU_TITLES = (
    (True, "Copy", QKeySequence.StandardKey.Copy),
    (False, "go to this location", None),
    (False, "Reveal in explorer", None),
    (False, "delete file from this location", None),
    (True, "", None),       # addSeparator
    (True, "Select All", QKeySequence.StandardKey.SelectAll),
)


def dir_type(dd: ag.DirData):
    """
    returns:
       '(L)' if folder is link to another folder,
       '(H)' if folder is hidden
       '(LH) if folder is link and is hidden
       empty string - otherwise
    """
    tt = f'{"L" if dd.is_link else ""}{"H" if dd.hidden else ""}'
    return f'({tt})' if tt else ''

class Locations(QTextBrowser):
    def __init__(self, parent = None) -> None:
        super().__init__(parent)
        self.file_id = 0
        self.branches = []
        self.names = defaultdict(list)

        self.cur_pos = QPoint()
        self.setTabChangesFocus(False)
        self.mousePressEvent = self.loc_menu

    def loc_menu(self, e: QMouseEvent):
        self.cur_pos = e.pos()
        if e.buttons() is Qt.MouseButton.LeftButton:
            self.select_line_under_mouse(self.cur_pos)
            return
        if e.buttons() is Qt.MouseButton.RightButton:
            txt_cursor = self.textCursor()
            if not txt_cursor.hasSelection():
                line = self.select_line_under_mouse(self.cur_pos)
            else:
                line = txt_cursor.selectedText()

            branch = self.names.get(line, False)
            menu = self.create_menu(branch)
            action = menu.exec(self.mapToGlobal(self.cur_pos))
            if action:
                {
                    MENU_TITLES[0][1]: self.copy,
                    MENU_TITLES[1][1]: self.go_file,
                    MENU_TITLES[2][1]: self.reveal_file,
                    MENU_TITLES[3][1]: self.delete_file,
                    MENU_TITLES[5][1]: self.selectAll,
                }[action.text()]()

    def get_branch(self, file_id: int=0) -> list:
        branches = list(self.names.values())
        if file_id == 0:
            return branches[0][0] if len(branches) > 0 else []
        for blist in branches:
            for bb in blist:
                if bb[1] == file_id:
                    return bb[0]
        return []

    def go_file(self):
        key = self.select_line_under_mouse(self.cur_pos)
        value = self.names.get(key, False)
        branch = ','.join((str(i) for i in value[0][0]))
        ag.signals_.user_signal.emit(
            f'file-note: Go to file\\{value[0][1]}-{branch}'
        )

    def delete_file(self):
        key = self.select_line_under_mouse(self.cur_pos)
        branch = self.names.get(key, False)[0]
        ag.signals_.user_signal.emit(
            f'remove_file_from_location\\{branch[0][-1]},{branch[1]}'
        )

    def reveal_file(self):
        key = self.select_line_under_mouse(self.cur_pos)
        ag.signals_.user_signal.emit(
            f'file reveal\\{self.names.get(key, False)[0][1]}'
        )

    def select_line_under_mouse(self, pos: QPoint) -> QTextCursor:
        txt_cursor = self.cursorForPosition(pos)
        txt_cursor.select(QTextCursor.SelectionType.LineUnderCursor)
        sel_text = txt_cursor.selectedText().split(' \xa0'*4)[0]
        self.setTextCursor(txt_cursor)
        return sel_text

    def create_menu(self, branch) -> QMenu:
        menu = QMenu(self)
        actions = []
        for cond, name, key in MENU_TITLES:
            if cond or branch:
                if name:
                    actions.append(QAction(name, self))
                    if key:
                        actions[-1].setShortcut(key)
                else:
                    actions.append(QAction(self))
                    actions[-1].setSeparator(True)
        menu.addActions(actions)
        return menu

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
                [(dd.id, dir_type(dd), dd.file_id), dd.parent_id]
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
        def add_dir_parent(d_data: ag.DirData, tt: list) -> list:
            ss = tt[:-1]
            tt[-1] = (d_data.id, dir_type(d_data))
            tt.append(d_data.parent_id)
            return ss

        curr = 0
        while 1:
            if curr >= len(self.branches):
                break
            tt = self.branches[curr]

            while 1:
                if tt[-1] == 0:
                    break
                parents = db_ut.dir_parents(tt[-1])
                first = True
                for pp in parents:
                    qq = ag.DirData(*pp)
                    if first:
                        ss = add_dir_parent(qq, tt)
                        first = False
                        continue
                    self.branches.append(
                        [*ss, (qq.id, dir_type(qq)), qq.parent_id]
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
