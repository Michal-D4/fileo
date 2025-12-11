from datetime import datetime
import hashlib
from pathlib import Path

from PyQt6.QtCore import pyqtSignal, QObject, pyqtSlot

from ..core import app_globals as ag, db_ut, reports

def report_duplicates() -> dict[list]:
    rep_creator = reports.Duplicates()
    return rep_creator.get_report()

def sha256sum(filename: Path) -> str:
    h  = hashlib.sha256()
    b  = bytearray(128*1024)
    mv = memoryview(b)
    try:
        with open(filename, 'rb', buffering=0) as f:
            while n := f.readinto(mv):
                h.update(mv[:n])
        return h.hexdigest()
    except (FileNotFoundError, PermissionError):
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
            db_ut.delete_not_exist_file(f_id)

def update_touched_files():
    last_scan = ag.get_db_setting('LAST_SCAN_OPENED', ag.ZERO_DATE)
    ag.save_db_settings(LAST_SCAN_OPENED=int(datetime.now().timestamp()))
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
            db_ut.delete_not_exist_file(f_id)

class worker(QObject):
    finished = pyqtSignal()

    def __init__(self, func, parent = None) -> None:
        super().__init__(parent)
        self.runner = func

    @pyqtSlot()
    def run(self):
        self.runner()
        self.finished.emit()
