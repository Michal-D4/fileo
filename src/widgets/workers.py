from datetime import datetime
import hashlib
from loguru import logger
from pathlib import Path
import PyPDF2

from PyQt6.QtCore import pyqtSignal, QObject, pyqtSlot

from ..core import app_globals as ag, db_ut, reports

def report_duplicates() -> dict[list]:
    rep_creator = reports.Duplicates()
    return rep_creator.get_report()

def find_lost_files():
    db_ut.lost_files()

def sha256sum(filename: Path) -> str:
    h  = hashlib.sha256()
    b  = bytearray(128*1024)
    mv = memoryview(b)
    try:
        with open(filename, 'rb', buffering=0) as f:
            while n := f.readinto(mv):
                h.update(mv[:n])
        return h.hexdigest()
    except (FileNotFoundError, PermissionError) as ex:
        return ''

def update0_files():
    files = db_ut.recent_loaded_files()
    for f_id, file, path in files:
        if ag.stop_thread:
            break
        pp = Path(path) / file
        f_hash = sha256sum(pp)
        if f_hash:
            db_ut.update_file_data(f_id, pp.stat(), f_hash)
        else:
            db_ut.delete_not_exest_file(f_id)

def update_touched_files():
    last_scan = ag.get_setting('LAST_SCAN_OPENED', -62135596800)
    ag.save_settings(
        LAST_SCAN_OPENED=int(datetime.now().timestamp())
    )
    files = db_ut.files_toched(last_scan)
    for f_id, file, path, hash0 in files:
        if ag.stop_thread:
            break
        pp = Path(path) / file
        f_hash = sha256sum(pp)
        if f_hash:
            if f_hash != hash0:
                db_ut.update_file_data(f_id, pp.stat(), f_hash)
        else:
            db_ut.delete_not_exest_file(f_id)

def update_pdf_files():
    files = db_ut.get_pdf_files()
    for f_id, file, path, in files:
        if ag.stop_thread:
            break
        pp = Path(path) / file
        try:
            pdf_file_update(f_id, pp)
        except FileNotFoundError as e:
            db_ut.delete_not_exest_file(f_id)

def pdf_file_update(id: int, file: str):
    with (open(file, "rb")) as pdf_file:
        fr = PyPDF2.PdfReader(pdf_file, strict=False)
        try:
            pp = len(fr.pages)
        except KeyError:
            pp = -1

        db_ut.update_files_field(id, 'pages', pp)
        fi = fr.metadata
        if not fi:
            return
        if '/Author' in fr.metadata.keys():
            tmp = split_authors(fi['/Author'])
            add_authors(id, tmp)
        if '/CreationDate' in fr.metadata.keys():
            save_published_date(id, fi['/CreationDate'])

def save_published_date(id: int, pdate:str):
        dd = pdate[2:] if pdate.startswith('D:') else pdate
        dt = datetime.strptime(dd[:6],"%Y%m")
        db_ut.update_files_field(id, 'published', int(dt.timestamp()))

def split_authors(names: str):
    """
    authors may be separated either with semicolon or with comma
    not both, first is semicolon - comma may be inside name
    """
    def inner_split(dlm: str):
        tmp = names.strip().strip(dlm).split(dlm)
        return dlm in names, tmp

    splitted, tmp = inner_split(';')
    if splitted:
        return tmp
    return inner_split(',')[1]

def add_authors(id: int, names: list[str]):
    for name in names:
        if nn := name.strip():
            db_ut.add_author(id, nn)

class worker(QObject):
    finished = pyqtSignal()

    def __init__(self, func, parent = None) -> None:
        super().__init__(parent)
        self.runner = func

    @pyqtSlot()
    def run(self):
        self.runner()
        self.finished.emit()
