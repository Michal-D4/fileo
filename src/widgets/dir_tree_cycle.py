# from loguru import logger
from collections import defaultdict
from ..core import app_globals as ag, db_ut


class removeDirCycle():
    def __init__(self):
        self.adj_list = {}  # children id for each dir
        self.break_edge = None

    def construct_adj_list(self):
        sql = 'select parent, id from parentdir'
        for u,v in ag.db.conn.cursor().execute(sql):
            if u not in self.adj_list:
                self.adj_list[u] = []
            self.adj_list[u].append(v)

    def aux_cyclic(self, u: int) -> int:
        """ DFS-based cycle detection """
        if self.in_stack[u]:
            return True

        if self.visited[u]:
            return False

        self.in_stack[u] = True
        self.visited[u] = True

        for x in self.adj_list.get(u, []):
            if self.aux_cyclic(x):
                if not self.break_edge:
                    self.break_edge = (u, x)
                return True

        self.in_stack[u] = False
        return False

    def remove_cycles(self):
        def break_cycle():
            if self.break_edge:
                u,v = self.break_edge
                self.adj_list[u].remove(v)
                db_ut.break_link(v, u)

        def find_break_edge() -> bool:
            self.visited = defaultdict(lambda: False)
            self.in_stack = defaultdict(lambda: False)
            self.break_edge = None
            for u in self.adj_list:
                if not self.visited[u] and self.aux_cyclic(u):
                    return True
            return False

        while find_break_edge():
            find_break_edge()
            break_cycle()
