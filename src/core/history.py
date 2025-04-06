# from loguru import logger
from datetime import datetime

from . import app_globals as ag, db_ut


class History(object):
    def __init__(self, limit: int = 20):
        self.limit: int = limit
        self.hist = {}
        self.curr: str = ''
        self.is_hist = True

    def check_remove(self):
        kk = []
        for k,v in self.hist.items():
            vv = ['0', *v[0].split(',')]
            for i in range(len(vv)-1):
                if db_ut.not_parent_child(vv[i], vv[i+1]):
                    kk.append(k)
                    break

        for k in kk:
            self.hist.pop(k)

    def set_history(self, hist: list, curr: str):
        self.hist = dict(zip(*hist))
        self.curr = curr

        ag.signals_.user_signal.emit(
            f'enable_next_prev\\{self.enable_next_prev()}'
        )

    def set_limit(self, limit: int):
        self.limit: int = limit
        if len(self.hist) > limit:
            self.trim_to_limit()

    def trim_to_limit(self):
        kk = list(self.hist.keys())
        kk.sort()
        for i in range(len(self.hist) - self.limit):
            self.hist.pop(kk[i])

    def get_current(self):
        if not self.curr:
            return []
        self.is_hist = True
        return (*(int(x) for x in self.hist[self.curr][0].split(',')), self.hist[self.curr][1])

    def next_dir(self) -> list:
        kk: list = sorted(self.hist)
        i = kk.index(self.curr)
        if i < len(self.hist)-1:
            self.curr = kk[i+1]

        ag.signals_.user_signal.emit(f'enable_next_prev\\{self.enable_next_prev()}')
        return self.get_current()

    def prev_dir(self) -> list:
        kk: list = sorted(self.hist)
        i = kk.index(self.curr)
        if i > 0:
            self.curr = kk[i-1]

        ag.signals_.user_signal.emit(f'enable_next_prev\\{self.enable_next_prev()}')
        return self.get_current()

    def enable_next_prev(self) -> str:
        res = ('no', 'yes')

        if len(self.hist) == 0:
            return 'no,no'
        if len(self.hist) == 1:
            self.curr = next(iter(self.hist))
            return "no,yes"
        return f'{res[self.curr < max(self.hist.keys())]},{res[self.curr > min(self.hist.keys())]}'

    def add_item(self, branch: list):
        if not branch[:-1]:
            return

        def find_key() -> str:
            for k, v in self.hist.items():
                if v[0] == val:
                    return k
            return ''

        def set_curr_history_item():
            if old_key:
                if self.is_hist:
                    return
                self.hist.pop(old_key)
            else:
                if len(self.hist) == self.limit:
                    self.hist.pop(min(self.hist.keys()))

            key = str(datetime.now().replace(microsecond=0))
            if len(self.hist) > 1:
                self.curr = key
            self.hist[key] = val, branch[-1]

        val = ','.join((str(x) for x in branch[:-1]))
        old_key = find_key()
        set_curr_history_item()

        self.is_hist = False

        ag.signals_.user_signal.emit(f'enable_next_prev\\{self.enable_next_prev()}')

    def get_history(self) -> list:
        if not self.curr and self.hist:
            self.curr = next(iter(self.hist))
        return (list(self.hist.keys()), list(self.hist.values())), self.curr
