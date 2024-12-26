from datetime import datetime

from . import app_globals as ag


class History(object):
    def __init__(self, limit: int = 20):
        self.limit: int = limit
        self.hist = {}
        self.curr: str = ''
        self.is_hist = False

    def set_history(self, hist: list, curr: str):
        self.hist = dict(zip(*hist))
        self.curr = curr

        ag.signals_.user_signal.emit(
            f'enable_next_prev\\{self.has_next()},{self.has_prev()}'
        )

    def set_limit(self, limit: int):
        self.limit: int = limit
        if len(self.hist) > limit:
            self.trim_to_limit()

    def trim_to_limit(self):
        kk = list(self.hist.keys())
        kk.sort(reverse=True)
        for i in range(len(self.hist) - self.limit):
            self.hist.pop(kk[i])

    def get_current(self):
        if not self.hist or not self.curr:
            return []
        return [int(i) for i in self.hist[self.curr].split(',')]

    def next_dir(self) -> list:
        kk: list = list(self.hist.keys())
        kk.sort()

        i = kk.index(self.curr)
        if i < len(self.hist)-1:
            self.curr = kk[i+1]

        ag.signals_.user_signal.emit(
            f'enable_next_prev\\{self.has_next()},yes'
        )
        self.is_hist = True
        return self.get_current()

    def prev_dir(self) -> list:
        kk: list = list(self.hist.keys())
        kk.sort()

        i = kk.index(self.curr)
        if i > 0:
            self.curr = kk[i-1]

        ag.signals_.user_signal.emit(
            f'enable_next_prev\\yes,{self.has_prev()}'
        )
        self.is_hist = True
        return self.get_current()

    def has_next(self) -> str:
        if len(self.hist) == 0:
            return 'no'
        return 'yes' if max(self.hist.keys()) > self.curr else 'no'

    def has_prev(self) -> str:
        if len(self.hist) == 0:
            return 'no'
        return 'yes' if min(self.hist.keys()) < self.curr else 'no'

    def add_item(self, new: list):
        def del_if_exists():
            vv = list(self.hist.values())
            if val in vv:
                for k, v in self.hist.items():
                    if v == val:
                        self.hist.pop(k)
                        break
            else:
                if len(self.hist) == self.limit:  # if limit exceeded
                    self.hist.pop(min(list(self.hist.keys())))

        key = str(datetime.now().replace(microsecond=0))
        val = ','.join((str(x) for x in new))

        if self.is_hist:
            self.is_hist = False
            return

        if not self.curr:
            self.curr = key
            self.hist[key] = val
            return

        del_if_exists()
        self.hist[key] = val
        self.curr = key

        ag.signals_.user_signal.emit(
            f'enable_next_prev\\no,{self.has_prev()}'
        )

    def get_history(self) -> list:
        return [(list(self.hist.keys()), list(self.hist.values())), self.curr]
