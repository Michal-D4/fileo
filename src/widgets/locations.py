from loguru import logger

from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import (
    QMouseEvent, QTextCursor, QAction,
    QKeySequence,
)
from PyQt6.QtWidgets import QTextBrowser, QMenu

from ..core import icons, app_globals as ag, db_ut

MENU_TITLES = (
    (True, "Copy", QKeySequence.StandardKey.Copy),
    (False, "go to this location", None),
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
        self.cur_branch = []
        self.branches = []
        self.dirs = []
        self.names = {}

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
                txt_cursor = self.select_line_under_mouse(self.cur_pos)
            line = txt_cursor.selectedText()
            branch = self.names.get(line, False)
            menu = self.create_menu(branch)
            action = menu.exec(self.mapToGlobal(self.cur_pos))
            if action:
                {
                    MENU_TITLES[0][1]: self.copy,
                    MENU_TITLES[1][1]: self.go_file,
                    MENU_TITLES[2][1]: self.delete_file,
                    MENU_TITLES[4][1]: self.selectAll,
                }[action.text()]()

    def go_file(self):
        txt_cursor = self.select_line_under_mouse(self.cur_pos)
        branch = self.names.get(txt_cursor.selectedText(), False)
        ag.signals_.user_signal.emit(
            f'file-note: Go to file/{self.file_id}-{branch}'
        )
        self.set_file_id(self.file_id)

    def delete_file(self):
        txt_cursor = self.select_line_under_mouse(self.cur_pos)
        branch = self.names.get(txt_cursor.selectedText(), False)
        ag.signals_.user_signal.emit(
            f'remove_file_from_location/{branch[-1]},{self.file_id}'
        )

    def select_line_under_mouse(self, pos: QPoint) -> QTextCursor:
        txt_cursor = self.cursorForPosition(pos)
        txt_cursor.select(QTextCursor.SelectionType.LineUnderCursor)
        self.setTextCursor(txt_cursor)
        return txt_cursor

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

    def set_current_branch(self, branch):
        self.cur_branch = branch

    def set_file_id(self, id: int):
        self.file_id = id
        self.get_leaves()
        self.build_branches()
        self.build_branch_data()
        self.show_branches()

    def get_leaves(self):
        dir_ids = db_ut.get_file_dir_ids(self.file_id)
        self.get_file_dirs(dir_ids)
        self.branches.clear()
        for dd in self.dirs:
            self.branches.append([(dd.id, dir_type(dd)), dd.parent_id])

    def get_file_dirs(self, dir_ids):
        self.dirs.clear()
        for id in dir_ids:
            parents = db_ut.dir_parents(id[0])
            for pp in parents:
                self.dirs.append(ag.DirData(*pp))

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

    def show_branches(self):
        txt = [
            '<HEAD><STYLE type="text/css"> p, li {text-align: left; '
            'text-indent:-28px; line-height: 66%} </STYLE> </HEAD> <BODY> '
        ]
        for key, val in self.names.items():
            if val == self.cur_branch:
                tmp = f'<ul><li type="circle">{key}</li></ul>'
            else:
                tmp = f'<p><blockquote>{key}</p>'
            txt.append(tmp)

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
        for id in tt:
            name = db_ut.get_dir_name(id[0])
            ww.append(f'{name}{id[1]}')
            vv.append(id[0])
        return ' > '.join(ww), vv
