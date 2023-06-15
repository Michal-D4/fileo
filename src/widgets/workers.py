from datetime import datetime
import hashlib
from loguru import logger
from pathlib import Path
import PyPDF2

from PyQt6.QtCore import pyqtSignal, QObject, pyqtSlot

from ..core import app_globals as ag, db_ut, low_bk

def find_lost_files() -> bool:
    return db_ut.lost_files()

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
    for id, file, path in files:
        if ag.stop_thread:
            break
        pp = Path(path) / file
        hash = sha256sum(pp)
        db_ut.update_file_data(id, pp.stat(), hash)

def update_touched_files():
    last_scan = low_bk.get_setting('LAST_SCAN_OPENED', -62135596800)
    low_bk.save_settings(
        LAST_SCAN_OPENED=int(datetime.now().timestamp())
    )
    files = db_ut.files_toched(last_scan)
    for id, file, path, hash0 in files:
        if ag.stop_thread:
            break
        pp = Path(path) / file
        hash = sha256sum(pp)
        if hash != hash0:
            db_ut.update_file_data(id, pp.stat(), hash)

def update_pdf_files():
    files = db_ut.get_pdf_files()
    for id, file, path, in files:
        if ag.stop_thread:
            break
        pp = Path(path) / file
        try:
            pdf_file_update(id, pp)
        except FileNotFoundError as e:
            # logger.info(f'{e}')
            pass

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