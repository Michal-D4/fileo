from loguru import logger
import apsw
from dataclasses import dataclass
from enum import Enum, unique
import pickle
from pathlib import Path
from typing import TYPE_CHECKING

from PyQt6.QtWidgets import QTreeView, QMessageBox

if TYPE_CHECKING:
    from .compact_list import aBrowser
    from .sho import shoWindow
    from ..widgets.file_data import fileDataHolder
    from ..widgets.filter_setup import FilterSetup
    from .history import History
    from ..widgets.fold_container import FoldState


def app_name() -> str:
    return "fileo"

def app_version() -> str:
    """
    if version changed here then also change it in the "pyproject.toml" file
    """
    return '1.3.02'

entry_point: Path = None
app: 'shoWindow' = None
dir_list: QTreeView = None
tag_list: 'aBrowser' = None
ext_list: 'aBrowser' = None
file_list: QTreeView = None
author_list: 'aBrowser' = None
file_data: 'fileDataHolder' = None
filter_dlg: 'FilterSetup' = None
fold_states: 'list[FoldState]' = None
buttons = []
note_buttons = []
history: 'History' = None
file_history = []
single_instance = False
stop_thread = False

@unique
class appMode(Enum):    # better name is fileListMode
    DIR = 1
    FILTER = 2
    FILTER_SETUP = 3
    HISTORY_FILES = 4
    FOUND_FILES = 5
    FILE_BY_REF = 6

    def __repr__(self) -> str:
        return f'{self.name}:{self.value}'

first_mode = appMode.DIR
mode = appMode.DIR

def set_mode(new_mode: appMode):
    global mode, first_mode
    if new_mode is mode:
        return
    if mode.value <= appMode.HISTORY_FILES.value:
        first_mode = mode
    mode = new_mode

    app.ui.app_mode.setText(mode.name)

def switch_first_mode():
    global mode, first_mode
    if mode.value >= appMode.HISTORY_FILES.value:
        old_mode, mode = mode, first_mode
        app.ui.app_mode.setText(mode.name)

        signals_.app_mode_changed.emit(old_mode.value)

@dataclass(slots=True)
class DB():
    path: str = ''
    conn: apsw.Connection = None
    restore: bool = True

    def __repr__(self):
        return f'(path: {self.path}, conn: {self.conn}, restore: {self.restore})'

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
    is_link: bool
    hidden: bool
    file_id: int = 0
    tool_tip: str = ''

    def __post_init__(self):
        self.is_link = bool(self.is_link)
        self.hidden = bool(self.hidden)

    def __repr__(self) -> str:
        return (
            f'DirData(parent_id={self.parent_id}, id={self.id}, '
            f'is_link={bool(self.is_link)}, hidden={bool(self.hidden)}, '
            f'file_id={self.file_id}, tool_tip={self.tool_tip})'
        )

@dataclass(slots=True)
class FileData():
    id: int = 0
    ext_id: int = 0
    path: int = 0

    def __repr__(self) -> str:
        return f'(file_id={self.id}, ext_id={self.ext_id}, path_id={self.path})'

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

def add_history_file(id_: int):
    """
    id_ - file id, valid value > 0
    """
    if id_ < 1 or file_history and id_ == file_history[-1]:
        return
    try:
        i = file_history.index(id_)
        file_history.pop(i)
    except ValueError:
        pass

    file_history.append(id_)

def show_message_box(
        title: str, msg: str,
        custom_btns=None,
        btn: QMessageBox.StandardButton = QMessageBox.StandardButton.Close,
        icon: QMessageBox.Icon = QMessageBox.Icon.Information,
        details: str = '') -> int:
    dlg = QMessageBox(app)
    dlg.setWindowTitle(title)
    dlg.setText(msg)
    dlg.setDetailedText(details)

    if custom_btns:
        btns = []
        for btn in custom_btns:
            btns.append(dlg.addButton(*btn))
    else:
        dlg.setStandardButtons(btn)
    dlg.setIcon(icon)

    return dlg.exec()

# only this instance of AppSignals should be used anywhere in the application
from .app_signals import AppSignals
signals_ = AppSignals()
