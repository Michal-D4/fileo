from loguru import logger
from dataclasses import dataclass

from . import app_globals as ag, db_ut

@dataclass(slots=True)
class Item():
    path: list = tuple()
    file_id: int = 0

    def __post_init__(self):
        if isinstance(self.path, str):
            self.path = [int(i) for i in self.path.split(',')]

class History(object):
    def __init__(self, limit: int = 20):
        self.curr: Item = Item()
        self.limit: int = limit
        self.next_ = []
        self.prev = []

    def set_history(self, next_: list, prev: list, curr: Item):
        """
        used to restore history on startup
        """
        self.next_ = next_
        self.prev = prev
        self.curr = curr
        # logger.info(f'{self.next_=}')
        # logger.info(f'{self.prev=}')
        # logger.info(f'{self.curr=}')
        # logger.info(f'{self.limit=}')
        ag.signals_.user_signal.emit(
            f'enable_next_prev/{self.has_next()},{self.has_prev()}'
        )

    def set_limit(self, limit: int):
        self.limit: int = limit
        if len(self.next_) > limit:
            self.next_ = self.next_[len(self.next_)-limit:]
        if len(self.prev) > limit:
            self.prev = self.prev[len(self.prev)-limit:]

    def next_dir(self) -> Item:
        if len(self.prev) >= self.limit:
            self.prev = self.prev[len(self.prev)-self.limit-1:]
        self.prev.append(self.curr)
        # logger.info(f'{self.prev=}')

        self.curr = self.next_.pop()
        # logger.info(f'{self.curr=}')
        ag.signals_.user_signal.emit(
            f'enable_next_prev/{self.has_next()},yes'
        )
        return self.curr

    def prev_dir(self) -> Item:
        if len(self.next_) >= self.limit:
            self.next_ = self.next_[len(self.next_)-self.limit-1:]
        self.next_.append(self.curr)
        # logger.info(f'{self.next_=}')

        self.curr = self.prev.pop()
        # logger.info(f'{self.curr=}')
        ag.signals_.user_signal.emit(
            f'enable_next_prev/yes,{self.has_prev()}'
        )
        return self.curr

    def set_file_id(self, row_no: int):
        '''
        set file_id in the history item to be left
        '''
        if self.curr.path and row_no >= 0:
            self.curr.file_id = row_no
            db_ut.update_file_id(self.curr.path, row_no)

    def has_next(self) -> str:
        return 'yes' if self.next_ else 'no'

    def has_prev(self) -> str:
        return 'yes' if self.prev else 'no'

    def add_item(self, path, file_id):
        # logger.info(f'{path=}, {file_id=}')
        if self.curr:
            if len(self.prev) >= self.limit:
                self.prev = self.prev[len(self.prev)-self.limit-1:]
            self.prev.append(self.curr)
            # logger.info(f'{self.prev=}')
        self.next_.clear()
        ag.signals_.user_signal.emit(
            f'enable_next_prev/no,{self.has_prev()}'
        )
        self.curr = Item(path, file_id)
        # logger.info(f'{self.curr=}')

    def get_history(self) -> list:
        """
        used to save histiry on close
        """
        self.set_file_id(ag.file_list.currentIndex().row())
        return [self.next_, self.prev, self.curr]
