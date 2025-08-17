# from loguru import logger
import apsw
from dataclasses import dataclass
from enum import Enum, unique
import pickle
from typing import TYPE_CHECKING

from PyQt6.QtCore import QModelIndex
from PyQt6.QtWidgets import QMessageBox, QStyle

from ..widgets.cust_msgbox import CustomMessageBox

if TYPE_CHECKING:
    from PyQt6.QtWidgets import QTreeView
    from .compact_list import aBrowser
    from .sho import shoWindow
    from ..widgets.file_data import fileDataHolder
    from ..widgets.filter_setup import FilterSetup
    from .history import History
    from ..widgets.fold_container import foldGrip


def app_name() -> str:
    return "fileo"

def app_version() -> str:
    """
    if version changed here then also change it in the "pyproject.toml" file
    """
    return '1.3.50'

app: 'shoWindow' = None
dir_list: 'QTreeView' = None
file_list: 'QTreeView' = None
tag_list: 'aBrowser' = None
ext_list: 'aBrowser' = None
author_list: 'aBrowser' = None
file_data: 'fileDataHolder' = None
filter_dlg: 'FilterSetup' = None
fold_grips: 'list[foldGrip]' = None
popups = {}

buttons = []
note_buttons = []
history: 'History' = None
recent_files = []
recent_files_length = 20
stop_thread = False
start_thread = None

@unique
class appMode(Enum):
    DIR = 1
    FILTER = 2
    FILTER_SETUP = 3
    RECENT_FILES = 4
    FOUND_FILES = 5
    FILE_BY_REF = 6

    def __repr__(self) -> str:
        return f'{self.name}:{self.value}'

prev_mode = appMode.DIR
mode = appMode.DIR

def set_mode(new_mode: appMode):
    global mode, prev_mode
    if new_mode is mode:
        return
    if mode.value <= appMode.RECENT_FILES.value:
        prev_mode = mode

    mode = new_mode
    if prev_mode is mode:
        prev_mode = appMode.DIR

    app.ui.app_mode.setText(mode.name)

def switch_to_prev_mode():
    global mode, prev_mode
    if mode.value >= appMode.RECENT_FILES.value:
        old_mode, mode = mode, prev_mode
        app.ui.app_mode.setText(mode.name)

        signals_.app_mode_changed.emit(old_mode.value)

@dataclass(slots=True)
class DB():
    path: str = ''
    conn: apsw.Connection = None

    def __repr__(self):
        return f'(path: {self.path}, conn: {self.conn})'

db = DB()

class mimeType(Enum):
    folders = "folders"
    files_in = "files/drag-inside"
    files_out = 'files/drag-outside'
    files_uri = 'text/uri-list'

@dataclass(slots=True)
class DirData():
    parent_id: int
    id: int
    multy: bool = False
    hidden: bool = False
    file_id: int = 0
    tool_tip: str = None

    def __post_init__(self):
        self.multy = bool(self.multy)
        self.hidden = bool(self.hidden)

    def __repr__(self) -> str:
        return (
            f'DirData(parent_id={self.parent_id}, id={self.id}, '
            f'multy={self.multy}, hidden={self.hidden}, '
            f'file_id={self.file_id}, tool_tip={self.tool_tip})'
        )

def save_db_settings(**kwargs):
    """
    used to save settings on DB level
    """
    if not db.conn:
        return
    cursor: apsw.Cursor = db.conn.cursor()
    sql = "insert or replace into settings values (:key, :value);"

    for key, val in kwargs.items():
        cursor.execute(sql, {"key": key, "value": pickle.dumps(val)})

def get_db_setting(key: str, default=None):
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
    except Exception:
        vv = None

    return vv if vv else default

def define_branch(index: QModelIndex) -> list:
    """
    return branch - a list of node ids from root to index
    """
    if not index.isValid():
        return [0]
    item = index.internalPointer()
    branch = []
    while 1:
        u_dat = item.user_data()
        branch.append(u_dat.id)
        if u_dat.parent_id == 0:
            break
        item = item.parent()
    branch.reverse()
    branch.append(int(dir_list.isExpanded(index)))
    return branch

KB, MB, GB = 1024, 1048576, 1073741824
def human_readable_size(n):
    if n > GB:
        return f'{n/GB:.2f} Gb'
    if n > MB:
        return f'{n/MB:.2f} Mb'
    if n > KB:
        return f'{n/KB:.2f} Kb'
    return n

def add_recent_file(id_: int):
    """
    id_ - file id, valid value > 0
    """
    if id_ < 1:
        return
    try:    # remove if id_ already in recent_files
        i = recent_files.index(id_)
        recent_files.pop(i)
    except ValueError:
        pass

    recent_files.append(id_)
    if len(recent_files) > recent_files_length:
        recent_files.pop(0)

def show_message_box(
        title: str, msg: str,
        btn: QMessageBox.StandardButton = QMessageBox.StandardButton.Close,
        icon = QStyle.StandardPixmap.SP_MessageBoxInformation,
        details: str = '',
        callback=None):
    dlg = CustomMessageBox(msg, app)
    if callback:
        dlg.finished.connect(callback)
    dlg.set_title(title)
    dlg.set_buttons(btn)
    dlg.set_msg_icon(icon)
    dlg.set_details(details)
    dlg.open()
    return dlg

# only this instance of AppSignals should be used anywhere in the application
from .app_signals import AppSignals  # noqa: E402
signals_ = AppSignals()
