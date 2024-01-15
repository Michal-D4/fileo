from loguru import logger
from collections import defaultdict
from pathlib import Path

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

class sameFileNames():
    """
    only file name id taking into acount, without extension;
    include into report:
    file name, path, folder, modification date
    """
    def __init__(self) -> None:
        self.report = []
        self.create_rep()

    def create_rep(self):
        def create_dict(files):
            for ff in files:
                logger.info(ff)
                pp = Path(ff[0])
                res[pp.stem].append((pp.stem, pp.suffix, *ff[1:]))

        files = db_ut.files_4_report()

        res = defaultdict(list)
        create_dict(files)

        for val in res.values():
            if len(val) > 1:
                self.report.append(val)

    def get_report(self) -> list:
        return self.report
