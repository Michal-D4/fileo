from collections import defaultdict

from . import db_ut

class Duplicates():
    def __init__(self) -> None:
        self.report = defaultdict(list)
        self.create_rep()

    def create_rep(self):
        dups = db_ut.file_duplicates()
        for dd in dups:
            self.report[dd[0]].append(dd[1:])

    def get_report(self) -> dict[list]:
        return self.report