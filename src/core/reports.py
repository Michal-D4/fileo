from loguru import logger
from collections import defaultdict
from pathlib import Path

from . import db_ut

class Duplicates():
    def __init__(self) -> None:
        self.report = {}
        self.create_rep()

    def create_rep(self):
        def min_idx():
            """
            find index of the shortest path
            """
            d = len(str(xx[0][0]))
            k = -1
            for i, x in enumerate(xx[1:]):
                if len(str(x)) < d:
                    k, d = i, len(str(x[0]))
            return k+1

        dups = db_ut.file_duplicates()
        repo = defaultdict(list)
        for dd in dups:
            repo[dd[0]].append(
                (Path(dd[1]) / dd[2], dd[3])
            )

        # put the duplicate with the shortest path first
        for key, xx in repo.items():
            k = min_idx()
            self.report[key] = [*xx[k:], *xx[:k]]

    def get_report(self) -> dict[list]:
        return self.report

class sameFileNames():
    """
    only file name taking into acount, without extension;
    include into report:
    full file name, size, file_id, count
    """
    def __init__(self) -> None:
        self.report = defaultdict(list)
        self.create_rep()

    def create_rep(self):
        def create_dict(files):
            for name, ext, path, size, file_id, count in files:
                pp = Path(path) / '.'.join((name, ext))
                self.report[name].append((pp, size, file_id, count))

        files = db_ut.same_file_names_report()
        create_dict(files)

    def get_report(self) -> list:
        return self.report
