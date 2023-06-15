from collections import defaultdict
from dataclasses import dataclass
from enum import Enum, unique
from pathlib import Path
from typing import TYPE_CHECKING

from PyQt6.QtWidgets import QTreeView, QToolButton

from .app_signals import AppSignals
if TYPE_CHECKING:
    from .compact_list import aBrowser
    from .sho import shoWindow
    from ..widgets.file_notes import notesBrowser
    from ..widgets.filter_setup import FilterSetup
    from .history import History

# only this instance of AppSignals should be used anywhere in the application
signals_ = AppSignals()

app: 'shoWindow' = None
dir_list: QTreeView = None
tag_list: 'aBrowser' = None
ext_list: 'aBrowser' = None
file_list: QTreeView = None
author_list: 'aBrowser' = None
field_menu: QToolButton = None
notes: 'notesBrowser' = None
filter: 'FilterSetup' = None
history: 'History' = None
hist_folder = True
file_row = 0
file_path: Path = None
single_instance = False

db = { 'Path': '', 'Conn': None, 'restore': True }

class mimeType(Enum):
    folders = "folders"
    files = "files"
    uri = 'text/uri-list'

@unique
class appMode(Enum):
    DIR = 1
    FILTER = 2
    FILTER_SETUP = 3

@dataclass(slots=True)
class DirData():
    parent_id: int
    id: int
    is_copy: bool
    hidden: bool
    file_row: int = 0

    def __post_init__(self):
        self.is_copy = bool(self.is_copy)
        self.hidden = bool(self.hidden)

@dataclass(slots=True)
class FileData():
    id: int
    ext_id: int
    path: int

stop_thread = False
mode = appMode.DIR
section_resized: bool = False

drop_button = 0
drop_target = None
dropped_ids = []

setting_names = (     # DB settings only
    "AUTHOR_SEL_LIST",
    "COLUMN_WIDTH",
    "EXT_SEL_LIST",
    "FIELDS_STATE",
    "FILE_ID",
    "TAG_SEL_LIST",
    "TREE_PATH",
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
    "FILE_SORT_COLUMN",
    "FILE_SORT_ORDER",
    "SHOW_HIDDEN",
    "HISTORY",
    "SEARCH_FILE",
)

dyn_qss = defaultdict(list)
qss_params = {}