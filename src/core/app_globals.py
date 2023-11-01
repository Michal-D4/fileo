from loguru import logger
import apsw
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum, unique
from pathlib import Path
import pickle
from typing import TYPE_CHECKING

from PyQt6.QtWidgets import QTreeView, QToolButton

if TYPE_CHECKING:
    from .compact_list import aBrowser
    from .sho import shoWindow
    from ..widgets.file_data import fileDataHolder
    from ..widgets.filter_setup import FilterSetup
    from .history import History

GT = 10        # Grip Thickness
MOVE_THRESHOLD = 50


def app_name() -> str:
    return "fileo"

def app_version() -> str:
    """
    if version changed here then also change it in the "pyproject.toml" file
    """
    return '0.9.56'

PID: int = 0
TIME_CHECK = 5     # interval(sec) client sends message "it's active"
entry_point: str = ''
app: 'shoWindow' = None
dir_list: QTreeView = None
tag_list: 'aBrowser' = None
ext_list: 'aBrowser' = None
file_list: QTreeView = None
author_list: 'aBrowser' = None
file_data_holder: 'fileDataHolder' = None
filter_dlg: 'FilterSetup' = None
history: 'History' = None
hist_folder = True
file_path: Path = None
single_instance = False

@dataclass(slots=True)
class DB():
    path: str = ''
    conn: apsw.Connection = None
    restore: bool = True

    def __repr__(self):
        return f'path: {self.path}, restore: {self.restore!r}, {self.conn!r}'

db = DB()

class mimeType(Enum):
    folders = "folders"
    files_in = "files/drag-inside"
    files_out = 'files/drag-outside'
    files_uri = 'text/uri-list'

@unique
class appMode(Enum):
    DIR = 1
    FILTER = 2
    FILTER_SETUP = 3

@dataclass(slots=True)
class DirData():
    parent_id: int
    id: int
    is_link: bool
    hidden: bool
    file_row: int = 0

    def __post_init__(self):
        self.is_link = bool(self.is_link)
        self.hidden = bool(self.hidden)

@dataclass(slots=True)
class FileData():
    id: int
    ext_id: int
    path: int

stop_thread = False
mode = appMode.DIR
srch_list = False

drop_button = 0
drop_target = None
dropped_ids = []

setting_names = (     # DB settings only
    "APP_MODE",
    "AUTHOR_SEL_LIST",
    "EXT_SEL_LIST",
    "FILE_LIST_HEADER",
    "FILE_ID",
    "TAG_SEL_LIST",
    "DIR_CHECK",
    "TAG_CHECK",
    "IS_ALL",
    "EXT_CHECK",
    "AUTHOR_CHECK",
    "DATE_TYPE",
    "AFTER",
    "BEFORE",
    "AFTER_DATE",
    "BEFORE_DATE",
    "OPEN_CHECK",
    "OPEN_OP",
    "OPEN_VAL",
    "RATING_CHECK",
    "RATING_OP",
    "RATING_VAL",
    "LAST_SCAN_OPENED",
    "SHOW_HIDDEN",
    "HISTORY",
    "SEARCH_FILE",
)

fields = (
    'File Name', 'Open Date', 'rating', 'Open#', 'Modified',
    'Pages', 'Size', 'Published', 'Date of last note', 'Created',
)
tool_tips = (
    ",Last opening date,rating of file,number of file openings,"
    "Last modified date,Number of pages(in book),Size of file,"
    "Publication date(book),Date of last note,File creation date"
).split(',')
field_types = (
    'str', 'date', 'int', 'int', 'date',
    'int', 'int', 'date', 'date', 'date',
)

dyn_qss = defaultdict(list)
qss_params = {}

def save_settings(**kwargs):
    """
    used to save settings on DB level
    """
    if not db.conn:
        return
    cursor: apsw.Cursor = db.conn.cursor()
    sql = "update settings set value = :value where key = :key;"

    for key, val in kwargs.items():
        cursor.execute(sql, {"key": key, "value": pickle.dumps(val)})

def get_setting(key: str, default=None):
    """
    used to restore settings on DB level
    """
    if not db.conn:
        return default
    cursor: apsw.Cursor = db.conn.cursor()
    sql = "select value from settings where key = :key;"

    try:
        val = cursor.execute(sql, {"key": key}).fetchone()[0]
        vv = pickle.loads(val) if val else None
    except:
        vv = None

    return vv if vv else default

# only this instance of AppSignals should be used anywhere in the application
from .app_signals import AppSignals
signals_ = AppSignals()
