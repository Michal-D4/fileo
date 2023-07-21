from loguru import logger

from PyQt6.QtWidgets import QTextBrowser

from ..core import icons, app_globals as ag, db_ut


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
        self.dirs = []
        self.names = []

    def set_file_id(self, id: int):
        self.file_id = id
        self.get_locations()
        self.build_branches()
        self.build_branch_data()
        self.show_branches()

    def get_locations(self):
        dir_ids = db_ut.get_file_dir_ids(self.file_id)
        self.get_file_dirs(dir_ids)
        self.branches.clear()
        for dd in self.dirs:
            # logger.info(f'{dd=}')
            self.branches.append([(dd.id, dir_type(dd)), dd.parent_id])

    def get_file_dirs(self, dir_ids):
        self.dirs.clear()
        for id in dir_ids:
            parents = db_ut.dir_parents(id[0])
            for pp in parents:
                # logger.info(f'{id=}, {pp=}')
                self.dirs.append(ag.DirData(*pp))

    def build_branches(self):
        def add_dir_parent(qq: ag.DirData, tt: list) -> list:
            # logger.info(f'{qq=}, {tt=}')
            ss = tt[:-1]          # [*tt[:-1]] is the same as tt[:-1] ?
            tt[-1] = (qq.id, dir_type(qq))
            tt.append(qq.parent_id)
            return ss

        curr = 0
        # logger.info(f'{curr=}, {len(self.branches)=}')
        while 1:
            if curr >= len(self.branches):
                break
            tt = self.branches[curr]
            # logger.info(f'{tt=}')

            while 1:
                if tt[-1] == 0:
                    break
                parents = db_ut.dir_parents(tt[-1])
                first = True
                for pp in parents:
                    # logger.info(f'{pp}')
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
            '<table>',
        ]
        for a,b,c in self.names:
            # TODO create referencies to go to filder with popup menu
            txt.append(
                f'<tr><td>{a}</td>'
            )
        txt.append('</table>')
        self.setHtml(''.join(txt))

    def build_branch_data(self):
        self.names.clear()
        for bb in self.branches:
            self.names.append(self.branch_names(bb))

    def branch_names(self, bb: list) -> str:
        tt = bb[:-1]
        tt.reverse()
        is_link = 'Y' if bb[0][0] else ''
        hidden = 'Y' if bb[0][1] else ''
        ww = []
        for id in tt:
            name = db_ut.get_dir_name(id[0])
            ww.append(f'{name}{id[1]}')
        return ' > '.join(ww), is_link, hidden
