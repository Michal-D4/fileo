from loguru import logger

from . import app_globals as ag, db_ut


class History(object):
    def __init__(self, limit: int = 20):
        self.curr = []
        self.limit: int = limit
        self.next_ = []
        self.prev = []

    def set_history(self, next_: list, prev: list, curr: list):
        """
        used to restore history on startup
        """
        self.next_ = next_
        self.prev = prev
        self.curr = curr
        ag.signals_.user_signal.emit(
            f'enable_next_prev/{self.has_next()},{self.has_prev()}'
        )

    def set_limit(self, limit: int):
        self.limit: int = limit
        # logger.info(f'{limit=}, {len(self.next_)=}, {len(self.prev)=}')
        if len(self.next_) > limit:
            self.next_ = self.next_[len(self.next_)-limit:]
        if len(self.prev) > limit:
            self.prev = self.prev[len(self.prev)-limit:]

    def get_current(self):
        return self.curr

    def next_dir(self) -> list:
        if len(self.prev) >= self.limit:
            self.prev = self.prev[len(self.prev)-self.limit+1:]
        self.prev.append(self.curr)

        self.curr = self.next_.pop()
        ag.signals_.user_signal.emit(
            f'enable_next_prev/{self.has_next()},yes'
        )
        # logger.info(f'{self.curr=}, {self.prev=}')
        return self.curr

    def prev_dir(self) -> list:
        if len(self.next_) >= self.limit:
            self.next_ = self.next_[len(self.next_)-self.limit+1:]
        self.next_.append(self.curr)

        self.curr = self.prev.pop()
        ag.signals_.user_signal.emit(
            f'enable_next_prev/yes,{self.has_prev()}'
        )
        # logger.info(f'{self.curr=}, {self.next_=}')
        return self.curr

    def has_next(self) -> str:
        return 'yes' if self.next_ else 'no'

    def has_prev(self) -> str:
        return 'yes' if self.prev else 'no'

    def add_item(self, path):
        # logger.info(f'{path=}, {self.curr=}')
        if self.curr:
            if len(self.prev) >= self.limit:
                self.prev = self.prev[len(self.prev) - self.limit + 1:]
            self.prev.append(self.curr)
        self.next_.clear()
        self.curr = path
        ag.signals_.user_signal.emit(
            f'enable_next_prev/no,{self.has_prev()}'
        )

    def get_history(self) -> list:
        """
        used to save histiry on close
        """
        return [self.next_, self.prev, self.curr]
