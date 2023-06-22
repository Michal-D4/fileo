from loguru import logger
from collections import defaultdict

from . import app_globals as ag, db_ut

class Duplicates():
    def __init__(self) -> None:
        self.report = defaultdict(list)
        logger.info(self.report)
        self.create_rep()

    def create_rep(self):
        # self.report.clear()
        dups = db_ut.file_duplicates()
        for dd in dups:
            self.report[dd[0]].append(dd[1:])

    def get_report(self) -> dict[list]:
        return self.report