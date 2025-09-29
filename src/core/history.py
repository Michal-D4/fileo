# from loguru import logger

from . import app_globals as ag, db_ut


class History(object):
    def __init__(self, limit: int = 20):
        self.limit: int = limit
        self.branches = []
        self.flags = []
        self.curr: int = -1
        self.is_hist = False

    def set_current(self, curr: int) -> tuple:
        self.curr = curr
        self.is_hist = True
        ag.signals_.user_signal.emit('curr_history_folder')

    def history_changed(self):
        ag.signals_.user_signal.emit('history_changed')

    def check_remove(self):
        kk = []
        for k,v in enumerate(self.branches):
            vv = ['0', *v.split(',')]
            for i in range(len(vv)-1):
                if db_ut.not_parent_child(vv[i], vv[i+1]):
                    kk.append(k)
                    break

        if kk:
            for k in kk[::-1]:
                self.branches.pop(k)
                self.flags.pop(k)

            corr = sum((k <= self.curr) for k in kk)
            self.curr -= corr

    def set_history(self, hist: list|None):
        if not hist:
            return
        self.branches, self.flags, self.curr = hist
        self.is_hist = True

    def set_limit(self, limit: int):
        self.limit: int = limit
        if len(self.branches) > limit:
            self.trim_to_limit()
            self.history_changed()

    def trim_to_limit(self):
        def trim(x: list):
            tmp = x[to_trim:]
            x.clear()
            x.extend(tmp)

        to_trim = len(self.branches) - self.limit
        self.curr = max(0, self.curr-to_trim)
        trim(self.branches)
        trim(self.flags)

    def get_current(self) -> tuple:
        if self.curr == -1:
            return (0, 0)
        self.is_hist = True
        return (*(int(x) for x in self.branches[self.curr].split(',')), self.flags[self.curr])

    def next_dir(self):
        if self.curr < len(self.branches)-1:
            self.curr += 1

    def prev_dir(self):
        if self.curr > 0:
            self.curr -= 1

    def is_next_prev_enable(self) -> tuple:
        if len(self.branches) <= 1:
            return False, False
        return self.curr < len(self.branches)-1, self.curr > 0

    def add_item(self, branch: list):
        if not branch[:-1]:
            return

        def find_key() -> int:
            if val in self.branches:
                return self.branches.index(val)
            self.branches = self.branches[:self.curr+1]
            self.flags = self.flags[:self.curr+1]
            return -1

        def set_curr_history_item():
            if old_idx < 0:      # new history item
                if len(self.branches) >= self.limit:
                    self.branches.pop(0)
                    self.flags.pop(0)
            else:                # change order of history item
                if self.is_hist: # branch reached from history
                    return       # not change order of history item
                self.branches.pop(old_idx)
                self.flags.pop(old_idx)

            self.curr = len(self.branches)
            self.branches.append(val)
            self.flags.append(branch[-1])

        val = ','.join((str(x) for x in branch[:-1]))
        old_idx = find_key()
        set_curr_history_item()

        self.is_hist = False

        self.history_changed()

    def get_history(self) -> list:
        return self.branches, self.flags, self.curr
