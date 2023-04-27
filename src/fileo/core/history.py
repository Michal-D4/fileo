from loguru import logger
from dataclasses import dataclass

from PyQt6.QtCore import Qt

from . import app_globals as ag, db_ut

@dataclass(slots=True)
class Item():
    path: list
    file_id: int

    def __post_init__(self):
        if isinstance(self.path, str):
            self.path = [int(i) for i in self.path.split(',')]

class History(object):
    def __init__(self, limit: int = 20):
        self.curr: Item = None
        self.limit: int = limit
        self.next = []
        self.prev = []

    def set_history(self, next: list, prev: list, curr: Item):
        self.next = next
        self.prev = prev
        self.curr = curr
        ag.signals_.user_action_signal.emit(
            f'enable_next_prev/{self.has_next()},{self.has_prev()}'
        )

    def set_limit(self, limit: int):
        self.limit: int = limit
        if len(self.next) > limit:
            self.next = self.next[len(self.next)-limit:]
        if len(self.prev) > limit:
            self.prev = self.prev[len(self.prev)-limit:]

    def next_dir(self) -> Item:
        self.stack_append(self.prev)

        self.curr = self.next.pop()
        ag.signals_.user_action_signal.emit(
            f'enable_next_prev/{self.has_next()},yes'
        )
        return self.curr

    def prev_dir(self) -> Item:
        self.stack_append(self.next)

        self.curr = self.prev.pop()
        ag.signals_.user_action_signal.emit(
            f'enable_next_prev/yes,{self.has_prev()}'
        )
        return self.curr

    def stack_append(self, stack):
        if len(stack) == self.limit:
            stack = stack[:-(self.limit-1)]
        stack.append(self.curr)

    def set_file_id(self, row_no: int):
        '''
        set file_id in the history item to be left
        '''
        if self.curr:
            self.curr.file_id = row_no
            db_ut.update_file_id(self.curr.path, row_no)

    def has_next(self) -> str:
        return 'yes' if self.next else 'no'

    def has_prev(self) -> str:
        return 'yes' if self.prev else 'no'

    def add_item(self, path, file_id):
        if self.curr:
            self.stack_append(self.prev)
        self.next.clear()
        ag.signals_.user_action_signal.emit(
            f'enable_next_prev/no,{self.has_prev()}'
        )
        self.curr = Item(path, file_id)

    def get_history(self) -> list:
        self.set_file_id(ag.file_list.currentIndex().row())
        return [self.next, self.prev, self.curr]
