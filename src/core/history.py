# from loguru import logger

from . import app_globals as ag, db_ut


class History(object):
    def __init__(self, limit: int = 20):
        self.limit: int = limit
        self.branches = []
        self.flags = []
        self.curr: str = ''
        self.is_hist = False

    def check_remove(self):
        kk = []
        for k,v in enumerate(self.branches):
            vv = ['0', *v.split(',')]
            for i in range(len(vv)-1):
                if db_ut.not_parent_child(vv[i], vv[i+1]):
                    kk.append(k)
                    break

        for k in kk:
            self.branches.pop(k)
            self.flags.pop(k)

    def set_history(self, hist: list, curr: int):
        self.branches, self.flags = hist if hist else ([],[])
        self.curr = curr

        ag.signals_.user_signal.emit(
            f'enable_next_prev\\{self.enable_next_prev()}'
        )

    def set_limit(self, limit: int):
        self.limit: int = limit
        if len(self.branches) > limit:
            self.trim_to_limit()

    def trim_to_limit(self):
        def trim(x: list):
            tmp = x[to_trim:]
            x.clear()
            x.extend(tmp)

        to_trim = len(self.branches) - self.limit
        trim(self.branches)
        trim(self.flags)

    def get_current(self):
        if not self.branches:
            return []
        self.is_hist = True
        return (*(int(x) for x in self.branches[self.curr].split(',')), self.flags[self.curr])

    def next_dir(self) -> list:
        if self.curr < len(self.branches)-1:
            self.curr += 1
        ag.signals_.user_signal.emit(f'enable_next_prev\\{self.enable_next_prev()}')
        return self.get_current()

    def prev_dir(self) -> list:
        if self.curr > 0:
            self.curr -= 1
        ag.signals_.user_signal.emit(f'enable_next_prev\\{self.enable_next_prev()}')
        return self.get_current()

    def enable_next_prev(self) -> str:
        res = ('no', 'yes')

        if len(self.branches) == 0:
            return 'no,no'
        if len(self.branches) == 1:
            self.curr = 0
            return "no,yes"
        return f'{res[self.curr < len(self.branches)-1]},{res[self.curr > 0]}'

    def add_item(self, branch: list):
        if not branch[:-1]:
            return

        def find_key() -> int:
            if val in self.branches:
                return self.branches.index(val)
            return -1

        def set_curr_history_item():
            if old_idx < 0:      # new history item
                if len(self.branches) == self.limit:
                    self.branches.pop(0)
                    self.flags.pop(0)
            else:                # change order of history item
                if self.is_hist: # branch reached from history
                    return       # not change order of history item
                self.branches.pop(old_idx)
                self.flags.pop(old_idx)

            self.curr = len(self.branches)
            self.branches.append(val),
            self.flags.append(branch[-1])

        val = ','.join((str(x) for x in branch[:-1]))
        old_idx = find_key()
        set_curr_history_item()

        self.is_hist = False

        ag.signals_.user_signal.emit(f'enable_next_prev\\{self.enable_next_prev()}')

    def get_history(self) -> list:
        return (self.branches, self.flags), self.curr
