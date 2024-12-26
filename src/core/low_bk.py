from loguru import logger
import json
from pathlib import Path
import pickle
import re

from PyQt6.QtCore import (Qt, QSize, QModelIndex,
    pyqtSlot, QUrl, QDateTime, QFile, QTextStream,
    QIODeviceBase, QItemSelectionModel
)
from PyQt6.QtGui import QDesktopServices, QFocusEvent
from PyQt6.QtWidgets import (QApplication, QAbstractItemView,
    QFileDialog, QMessageBox,
)

from . import (db_ut, app_globals as ag, reports as rep, check_update as upd,
)
from .file_model import fileModel, fileProxyModel
from .dir_model import dirModel, dirItem
from ..widgets import about, preferences
from ..widgets.open_db import OpenDB
from ..widgets.scan_disk_for_files import diskScanner
from .. import tug
from .filename_editor import folderEditDelegate

MAX_WIDTH_DB_DIALOG = 340

fields = (
    'File Name', 'Open Date', 'rating', 'Open#', 'Modified',
    'Pages', 'Size', 'Published', 'Date of last note', 'Created',
)
field_types = (
    'str', 'date', 'int', 'int', 'date',
    'int', 'int', 'date', 'date', 'date',
)


def set_user_action_handlers():
    """
    run methods for user_action_signal
    :@param action: string to select handle method
    :@return: None
    """
    data_methods = {
        "Dirs Create folder": create_dir,
        "Dirs Create folder as child": create_child_dir,
        "Dirs Delete folder(s)": delete_folders,
        "Dirs Edit tooltip": edit_tooltip,
        "Dirs Toggle hidden state": toggle_hidden_state,
        "Dirs Import files": import_files,
        "tag_inserted": populate_tag_list,
        "ext inserted": populate_ext_list,
        "author_inserted": populate_author_list,
        "Files Copy file name(s)": copy_file_name,
        "Files Copy full file name(s)": copy_full_file_name,
        "Files Open file": open_current_file,
        "Open file by path": open_with_url,
        "double click file": double_click_file,
        "Files Remove file(s) from folder": remove_files,
        "Files Delete file(s) from DB": delete_files,
        "Files Reveal in explorer": open_folder,
        "Files Rename file": rename_file,
        "Files Export selected files": export_files,
        "filter_changed": filtered_files,
        "MainMenu New window": new_window,
        "MainMenu Create/Open DB": create_open_db,
        "MainMenu Select DB from list": show_db_list,
        "MainMenu Scan disk for files": scan_disk,
        "MainMenu About": show_about,
        "MainMenu Report files with same names": report_same_names,
        "MainMenu Preferences": set_preferences,
        "MainMenu Check for update": upd.check4update,
        "find_files_by_name": find_files_by_name,
        "srch_files_by_note": srch_files_by_note,
        "enable_next_prev": enable_next_prev,
        "Enable_buttons": enable_buttons,
        "file-note: Go to file": goto_edited_file,
        "remove_file_from_location": remove_file_from_location,
        "SaveEditState": save_note_edit_state,
        "show file": single_file,
        "file reveal": reveal_in_explorer,
        "Files Clear file history": clear_recent_files,
        "Files Remove selected from history": remove_files_from_recent,
        "show_recent_files": show_recent_files,
      }

    @pyqtSlot(str)
    def execute_action(action: str):
        pos = action.find("\\")
        act = action if pos == -1 else action[:pos]
        try:
            if pos == -1:
                data_methods[act]()
            else:
                data_methods[act](action[pos+1:].strip())
        except KeyError as err:
            ag.show_message_box(
                'Action not implemented',
                f'Action name "{err}" not implemented',
                icon=QMessageBox.Icon.Warning
            )

    return execute_action

def new_window(db_name: str=''):
    tug.save_app_setting(MainWindowGeometry=ag.app.normalGeometry())
    tug.new_window(db_name)

def clear_recent_files():
    ag.recent_files.clear()
    ag.switch_to_prev_mode()

def remove_files_from_recent():
    for idx in ag.file_list.selectionModel().selectedRows(0):
        ag.recent_files.remove(idx.data(Qt.ItemDataRole.UserRole).id)
    show_recent_files()

def save_db_list():
    db_open = tug.open_db if tug.open_db else OpenDB(ag.app)
    db_open.save_db_list(ag.db.path)

def show_db_list():
    """
    manage the list of db files,
    select DB to open
    """
    if tug.open_db:
        tug.open_db.close()
        return

    tug.open_db = OpenDB(ag.app)
    tug.open_db.move(48, 20)
    tug.open_db.resize(
        min(ag.app.width() // 2, MAX_WIDTH_DB_DIALOG),
        ag.app.height() - 60)
    tug.open_db.show()
    tug.open_db.listDB.setFocus()

def create_open_db():
    db_open = tug.open_db if tug.open_db else OpenDB(ag.app)
    db_open.add_db()

def init_db(db_path: str):
    if db_path:
        db_open = OpenDB(ag.app)
        db_open.open_db(db_path)

def scan_disk():
    """
    search for files with a given extension
    in the selected folder and its subfolders
    """
    if not ag.db.conn:
        return
    srch_files = diskScanner(ag.app)
    srch_files.move(
        (ag.app.width()-srch_files.width()) // 4,
        (ag.app.height()-srch_files.height()) // 4)
    srch_files.show()

def save_note_edit_state():
    ag.save_settings(
        NOTE_EDIT_STATE=ag.file_data.get_edit_state()
    )

def goto_edited_file(param: str):
    file_id, branch = param.split('-')
    if not branch:
        single_file(file_id)
        return
    idx = expand_branch(
        (int(it) for it in branch.split(','))
    )

    if idx.isValid():
        if ag.mode is not ag.appMode.DIR:
            prev = ag.mode.value
            ag.set_mode(ag.appMode.DIR)
            set_check_btn(ag.appMode.DIR)
            app_mode_changed(prev)
        ag.dir_list.setCurrentIndex(idx)
        ag.dir_list.scrollTo(idx, QAbstractItemView.ScrollHint.PositionAtCenter)

        set_current_file(int(file_id))

def set_check_btn(new_mode: ag.appMode):
    checkable_btn = {
        ag.appMode.DIR: ag.app.ui.btnDir,
        ag.appMode.FILTER: ag.app.ui.btnFilter,
        ag.appMode.FILTER_SETUP: ag.app.ui.btnFilterSetup,
    }

    # need loop to find button to uncheck
    for key, btn in checkable_btn.items():
        btn.setIcon(tug.get_icon(btn.objectName(), int(key is new_mode)))

    if new_mode.value < ag.appMode.RECENT_FILES.value:
        checkable_btn[new_mode].setChecked(True)
    ag.set_mode(new_mode)

def report_same_names():
    rep_creator = rep.sameFileNames()
    repo = rep_creator.get_report()
    if repo:
        save_same_names_report(repo)
    else:
        ag.show_message_box(
            'Files with same names',
            "No files with same names found",
        )

def save_same_names_report(rep: list):
    pp = Path('~/fileo/report').expanduser()
    path = Path(
        tug.get_app_setting('DEFAULT_REPORT_PATH', str(pp))
    ) / f"same_names.{ag.app.ui.db_name.text()}.log"
    with open(path, "w") as out:
        out.write(f'DB path: {ag.db.path}\n')
        out.write(
            'each line contains:\n    '
            '  file size, full file name\n'
        )
        for key, rr in rep.items():
            out.write(f"{'-='*20}- {key}\n")
            for f_name, size, *_ in rr:
                out.write(
                    f'{size:5}, {f_name} \n'
                )

    open_with_url(str(path))

def enable_buttons():   # when create connection to DB
    ag.app.ui.btn_search.setEnabled(True)
    ag.app.refresh_tree.setEnabled(True)
    ag.app.show_hidden.setEnabled(True)
    ag.app.collapse_btn.setEnabled(True)

def rename_file():
    idx: QModelIndex = ag.file_list.currentIndex()
    idx = ag.file_list.model().index(idx.row(), 0)
    ag.file_list.setCurrentIndex(idx)
    ag.file_list.edit(idx)

def enable_next_prev(param: str):
    nex_, prev = param.split(',')
    ag.app.btn_next.setDisabled(nex_ == 'no')
    ag.app.btn_prev.setDisabled(prev == 'no')

def srch_files_by_note(param: str):
    def srch_prepare():
        if is_re:
            prep = re.compile(expr) if case else re.compile(expr, re.IGNORECASE)
            return lambda x: prep.search(x)
        return lambda x: expr in x

    logger.info(f'{param=}')
    expr, is_re, case, word = param.split(',')
    srch_exp = srch_prepare()
    last_id = 0
    for fid, _, note in db_ut.get_all_notes():
        if fid == last_id:
            continue
        if srch_exp(note):
            db_ut.save_to_temp('files_by_note', fid)
            last_id = fid

    show_files(db_ut.get_file_by_note())
    model = ag.file_list.model()
    if model.rowCount():
        ag.app.ui.files_heading.setText(f'Found files, text in notes "{expr}"')
    else:
        ag.show_message_box('Search in notes',
            f'Text "{srch_exp}" not found in notes!',
            icon=QMessageBox.Icon.Warning)


def find_files_by_name(param: str):
    pp = param.split(',')
    ag.app.ui.files_heading.setText(f'Found files "{pp[0]}"')
    files = db_ut.get_files_by_name(pp[0], int(pp[1]), int(pp[2]))
    ag.set_mode(ag.appMode.FOUND_FILES)

    show_files(files)
    ag.file_list.setFocus()

def set_preferences():
    pref = preferences.Preferences(ag.app)
    pref.move(
        (ag.app.width()-pref.width()) // 3,
        (ag.app.height()-pref.height()) // 3
    )
    pref.show()

def show_about():
    dlg = about.AboutDialog(ag.app)
    dlg.move(
        (ag.app.width()-dlg.width()) // 3,
        (ag.app.height()-dlg.height()) // 3
    )
    dlg.show()

#region Common
def save_branch(index: QModelIndex):
    branch = define_branch(index)
    db_ut.save_branch_in_aux(pickle.dumps(branch))

def restore_branch() -> QModelIndex:
    val = db_ut.get_branch_from_aux()
    return expand_branch(pickle.loads(val) if val else [])

def define_branch(index: QModelIndex) -> list:
    """
    return branch - a list of node ids from root to index
    """
    if not index.isValid():
        return []
    item: dirItem = index.internalPointer()
    branch = []
    while 1:
        u_dat = item.user_data()
        branch.append(u_dat.id)
        item = item.parent()
        if u_dat.parent_id == 0:
            break
    branch.reverse()
    return branch

def get_dir_names_path(index: QModelIndex) -> list:
    """
    return:  a list of node names from root to index
    """
    item: dirItem = index.internalPointer()
    branch = []
    while item:
        if not item.parent():
            break
        name = item.data()
        branch.append(name)
        item = item.parent()
    branch.reverse()
    return branch

def expand_branch(branch: list) -> QModelIndex:
    model = ag.dir_list.model()
    parent = QModelIndex()
    item: dirItem = model.rootItem
    for it in branch:
        if parent.isValid():
            if not ag.dir_list.isExpanded(parent):
                ag.dir_list.setExpanded(parent, True)

        for i,child in enumerate(item.children):
            ud = child.user_data()
            if it == ud.id:
                parent = model.index(i, 0, parent)
                item = child
                break
        else:
            break    # outer loop

    return parent
#endregion

#region  Dirs
def set_dir_model():
    model: dirModel = dirModel()
    model.set_model_data()
    ag.dir_list.setModel(model)
    ag.dir_list.setFocus()

    ag.dir_list.selectionModel().selectionChanged.connect(ag.filter_dlg.dir_selection_changed)
    ag.dir_list.selectionModel().currentRowChanged.connect(cur_dir_changed)

def restore_selected_dirs():
    branches = ag.get_setting("SELECTED_DIRS", [])
    model = ag.dir_list.selectionModel()
    model.clearSelection()
    idx = QModelIndex()
    for br in branches:
        # logger.info(f'{br=}')
        idx = expand_branch(branch=br)
        model.select(idx, QItemSelectionModel.SelectionFlag.Select)
    model.setCurrentIndex(idx, QItemSelectionModel.SelectionFlag.Current)

@pyqtSlot(QModelIndex, QModelIndex)
def cur_dir_changed(curr_idx: QModelIndex, prev_idx: QModelIndex):
    def set_folder_path_label():
        if curr_idx.isValid():
            ag.app.ui.folder_path.setText('>'.join(get_dir_names_path(curr_idx)))

    def add_history_item():
        ag.history.add_item(
            define_branch(ag.dir_list.currentIndex())
        )

    ag.app.collapse_btn.setChecked(False)
    set_folder_path_label()

    if curr_idx.isValid() and ag.mode is ag.appMode.DIR:
        save_file_id(prev_idx)
        show_folder_files()
        add_history_item()

def dirlist_get_focus(e: QFocusEvent):
    if e.reason() is Qt.FocusReason.ActiveWindowFocusReason:
        return
    ag.switch_to_prev_mode()

def save_file_id(dir_idx: QModelIndex):
    """ save current file_id in dir (parentdir) table """
    if dir_idx.isValid():
        file_idx = ag.file_list.currentIndex()
        if file_idx.isValid():
            file_id = file_idx.data(Qt.ItemDataRole.UserRole).id
            u_dat = update_file_id_in_dir_model(file_id, dir_idx)
            db_ut.update_file_id(u_dat)

def update_file_id_in_dir_model(file_id: int, idx: QModelIndex) -> ag.DirData:
        model = ag.dir_list.model()
        dir_item = model.getItem(idx)
        u_data: ag.DirData = dir_item.userData
        u_data.file_id = file_id
        return u_data

def dir_view_setup():
    ag.dir_list.header().hide()
    icon_size = 12
    indent = 12
    ag.dir_list.setIconSize(QSize(icon_size, icon_size))
    ag.dir_list.setIndentation(indent)
    ag.dir_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
#endregion

#region  Files - setup, populate ...
@pyqtSlot(int)
def app_mode_changed(prev_mode: int):
    prev = ag.appMode(prev_mode)

    if not ag.db.conn:
        return
    # logger.info(f'{ag.mode=!r}, {prev=!r}')
    if (ag.mode is ag.appMode.FILTER_SETUP
        or ag.mode is prev):
        return

    if prev is ag.appMode.FILTER:
        ag.save_settings(
            FILTER_FILE_ROW=ag.file_list.currentIndex().row()
        )
    elif prev is ag.appMode.DIR:
        save_file_id(ag.dir_list.currentIndex())

    refresh_file_list()
    if ag.mode is ag.appMode.FILTER:
        row = ag.get_setting("FILTER_FILE_ROW", 0)
        idx = ag.file_list.model().index(row, 0)
        ag.file_list.setCurrentIndex(idx)
        ag.file_list.scrollTo(idx)

def refresh_file_list():
    if ag.mode is ag.appMode.DIR:
        show_folder_files()
    else:
        filtered_files()

@pyqtSlot()
def to_prev_folder():
    branch = ag.history.prev_dir()
    go_to_history_folder(branch)

@pyqtSlot()
def to_next_folder():
    branch = ag.history.next_dir()
    go_to_history_folder(branch)

def go_to_history_folder(branch: list):
    if not branch:
        return
    _history_folder(branch)

def _history_folder(branch: list):
    idx = expand_branch(branch)
    if idx.isValid():
        ag.dir_list.setCurrentIndex(idx)
        ag.dir_list.scrollTo(idx, QAbstractItemView.ScrollHint.PositionAtCenter)

def filtered_files():
    """
    create a list of files by filter
    """
    ag.app.ui.files_heading.setText('filtered files')
    files = ag.filter_dlg.get_file_list()
    show_files(files)

def show_folder_files():
    idx = ag.dir_list.currentIndex()
    if idx.isValid():
        ag.app.ui.files_heading.setText(
            f'files from folder "{idx.data(Qt.ItemDataRole.DisplayRole)}"'
        )
        u_dat: ag.DirData = idx.data(Qt.ItemDataRole.UserRole)

        files = db_ut.get_files(u_dat.id, u_dat.parent_id)

        show_files(files, u_dat.file_id)
    else:
        show_files([])

def show_recent_files():
    idx = expand_branch(ag.history.get_current())
    if idx.isValid():
        ag.dir_list.setCurrentIndex(idx)
    ag.app.ui.files_heading.setText('Recent files')
    files = get_recent_files()

    show_files(files)
    ag.file_list.setFocus()

def get_recent_files() -> list:
    ''' in LIFO order '''
    ag.set_mode(ag.appMode.RECENT_FILES)
    return (db_ut.get_file(id_) for id_ in ag.recent_files[::-1])

def show_files(files, cur_file: int = 0):
    """
    populate file's model
    :@param files - list of file
    :@param cur_file - set current file, 0 is on first line
    """
    ag.file_list.setSortingEnabled(
        ag.mode is not ag.appMode.RECENT_FILES
    )
    model = fill_file_model(files)
    set_file_model(model)
    ag.file_list.selectionModel().currentRowChanged.connect(current_file_changed)

    set_current_file(cur_file)

def single_file(file_id: str):
    if ag.mode is ag.appMode.DIR:
        save_file_id(ag.dir_list.currentIndex())
    elif ag.mode is ag.appMode.FILTER:
        ag.save_settings(
            FILTER_FILE_ROW=ag.file_list.currentIndex().row()
        )
    ag.set_mode(ag.appMode.FILE_BY_REF)
    ag.app.ui.files_heading.setText('single_file')

    show_files([db_ut.get_file(file_id)])
    ag.file_list.setFocus()

def fill_file_model(files) -> fileModel:
    model: fileModel = fileModel()

    for ff in files:
        if not ff[0]:
            continue
        ff1 = []
        for i,typ in enumerate(field_types):
            ff1.append(field_val(typ, ff[i]))

        filename = Path(ff[0])
        ff1.append(
            (filename.stem.lower(), filename.suffix.lower())
            if filename.suffix else
            (filename.stem.lower(),)
        )
        model.append_row(ff1, ag.FileData(*ff[-3:]))

    rows = model.rowCount()
    ag.app.ui.file_count.setText(f"files: {rows}")

    return model

def set_current_file(file_id: int):
    model: fileProxyModel = ag.file_list.model()
    if file_id == 0:
        ag.file_list.setCurrentIndex(model.index(0, 0))
        return

    idx = model.get_index_by_id(int(file_id))
    if idx.isValid():
        ag.file_list.setCurrentIndex(idx)
        ag.file_list.scrollTo(idx)
    else:
        ag.file_list.setCurrentIndex(model.index(0, 0))

def field_val(typ:str, val=None):
    if typ == "str":
        return val if val else ''
    if typ == "int":
        return int(val) if val else 0
    a = QDateTime()
    a.setSecsSinceEpoch(-62135596800 if val is None else val)
    return a

def set_file_model(model: fileModel):
    proxy_model = fileProxyModel()
    proxy_model.setSourceModel(model)
    proxy_model.setSortRole(Qt.ItemDataRole.UserRole+1)
    model.setHeaderData(0, Qt.Orientation.Horizontal, fields)
    ag.file_list.setModel(proxy_model)

@pyqtSlot(QModelIndex, QModelIndex)
def current_file_changed(curr: QModelIndex, prev: QModelIndex):
    if curr.isValid():
        ag.file_list.scrollTo(curr)
        ag.app.ui.current_filename.setText(file_name(curr))
        # logger.info(f'{curr.data(Qt.ItemDataRole.DisplayRole)}, {curr.row()=}')
        file_notes_show(curr)

def copy_file_name():
    files = []
    for idx in ag.file_list.selectionModel().selectedRows(0):
        files.append(file_name(idx))
    QApplication.clipboard().setText('\n'.join(files))

def copy_full_file_name():
    files = []
    for idx in ag.file_list.selectionModel().selectedRows(0):
        files.append(full_file_name(idx))
    QApplication.clipboard().setText('\n'.join(files))

def open_folder():
    idx = ag.file_list.currentIndex()
    if idx.isValid():
        path = full_file_name(idx)
        tug.reveal_file(str(Path(path)))
        ag.add_file_to_recent(idx.data(Qt.ItemDataRole.UserRole).id)

def reveal_in_explorer(file_id: int|str):
    path = db_ut.get_file_path(file_id)
    tug.reveal_file(str(Path(path)))

def full_file_name(index: QModelIndex) -> str:
    file_id = index.data(Qt.ItemDataRole.UserRole).id
    return db_ut.get_file_path(file_id)

def file_name(index: QModelIndex) -> str:
    if index.column():
        index = ag.file_list.model().index(index.row(), 0)
    return index.data(Qt.ItemDataRole.DisplayRole)

def double_click_file():
    idx = ag.file_list.currentIndex()
    if idx.isValid() and (idx.column() == 0):
        open_file_by_model_index(idx)

def open_current_file():
    idx = ag.file_list.currentIndex()
    if idx.isValid():
        open_file_by_model_index(idx)

def open_file_by_model_index(index: QModelIndex):
    file_id = index.data(Qt.ItemDataRole.UserRole).id
    cnt = db_ut.duplicate_count(file_id)
    if cnt[0] > 1:
        ag.show_message_box(
            "Duplicated file",
            (f"There are {cnt} files with the same context\n"
             "It is highly recommended to remove duplicate files;\n"
             "the file will not be opened."),
             icon=QMessageBox.Icon.Warning
        )
        return
    if open_with_url(full_file_name(index)):
        update_open_date(index)
    else:
        open_manualy(index)
    ag.add_file_to_recent(index.data(Qt.ItemDataRole.UserRole).id)

def open_with_url(path: str) -> bool:
    # logger.info(f'{path=}')
    url = QUrl()
    return QDesktopServices.openUrl(url.fromLocalFile(path))

def update_open_date(index: QModelIndex):
    id = index.data(Qt.ItemDataRole.UserRole).id
    ts = db_ut.update_opened_file(id)
    if ts > 0:
        ag.file_list.model().update_opened(ts, index)

def delete_files():
    """
    delete file from DB
    """
    if not ag.file_list.selectionModel().hasSelection():
        return

    res = ag.show_message_box(
        'delete file from DB',
        'Selected files will be deleted. Please confirm',
        btn=QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel,
        icon=QMessageBox.Icon.Question
    )

    if res == QMessageBox.StandardButton.Ok:
        edit_state = ag.file_data.get_edit_state()
        ed_file_id = edit_state[1] if edit_state[0] else 0
        row = ag.file_list.model().rowCount()
        skip_edited = False
        for idx in ag.file_list.selectionModel().selectedRows(0):
            del_file_id = idx.data(Qt.ItemDataRole.UserRole).id
            if del_file_id == ed_file_id:
                skip_edited = True
                continue
            row = min(row, idx.row())
            db_ut.delete_file(del_file_id)
        if skip_edited:
            ag.show_message_box(
                'Not deleted',
                f'File "{db_ut.get_file_name(ed_file_id)}", '
                'a note is editing')
        post_delete_file(row)

def remove_files():
    '''
    delete file from folder only
    '''
    row = ag.file_list.model().rowCount()
    for idx in ag.file_list.selectionModel().selectedRows(0):
        row = min(row, idx.row())
        id = idx.data(Qt.ItemDataRole.UserRole).id
        dir_id = get_dir_id(id)
        db_ut.delete_file_dir_link(id, dir_id)
    post_delete_file(row)

def remove_file_from_location(param: str):
    file_id, dir_id = param.split(',')
    db_ut.delete_file_dir_link(file_id, dir_id)
    # need branch instead of empty list []
    ag.file_data.set_data(int(file_id), [])

def get_dir_id(file: int) -> int:
    """
    in case of appMode.DIR - returns id of current folder
    otherwise - returns id of arbitrary folder contained current file
    """
    if ag.mode is ag.appMode.DIR or ag.filter_dlg.is_single_folder():
        dir_idx = ag.dir_list.currentIndex()
        dir_dat: ag.DirData = dir_idx.data(Qt.ItemDataRole.UserRole)
        return dir_dat.id

    return db_ut.get_dir_id_for_file(file)

def post_delete_file(row: int):
    refresh_file_list()
    model = ag.file_list.model()
    row -= int(row >= model.rowCount())

    idx = model.index(row, 0)
    ag.file_list.setCurrentIndex(idx)
    ag.file_list.scrollTo(idx)
#endregion

#region  export-import
def export_files():
    pp = Path('~/fileo/export').expanduser()
    path = tug.get_app_setting('DEFAULT_EXPORT_PATH', str(pp))
    file_name, ok = QFileDialog.getSaveFileName(parent=ag.app,
        caption='Save list of exported files',
        directory=str((Path(path) / 'untitled')),
        filter='File list (*.file_list *.json *.txt)'
    )

    if ok:
        fl = QFile(file_name)
        fl.open(QIODeviceBase.OpenModeFlag.WriteOnly)
        _export_files(QTextStream(fl))

def _export_files(out: QTextStream):
    for idx in ag.file_list.selectionModel().selectedRows(0):
        try:
            file_data = db_ut.get_export_data(idx.data(Qt.ItemDataRole.UserRole).id)
        except TypeError:
            continue
        out << f"{json.dumps(file_data)}\n"

def import_files():
    pp = Path('~/fileo/export').expanduser()
    path = tug.get_app_setting('DEFAULT_EXPORT_PATH', str(pp))
    file_name, ok = QFileDialog.getOpenFileName(ag.app,
        caption="Open file",
        directory=path,
        filter="File list (*.file_list *.json *.txt)")
    if ok:
        fp = QFile(file_name)
        fp.open(QIODeviceBase.OpenModeFlag.ReadOnly)
        _import_files(QTextStream(fp))

def _import_files(fp: QTextStream):
    branch = define_branch(ag.dir_list.currentIndex())
    exist_dir = 0

    while not fp.atEnd():
        line = fp.readLine()
        exist_dir = load_file(json.loads(line))

    if exist_dir > 0:
        branch.append(exist_dir)
        set_dir_model()
        idx = expand_branch(branch)
        ag.dir_list.setCurrentIndex(idx)
    else:
        show_folder_files()

def load_file(fl: dict) -> int:
    file_ = fl['file']
    f_path: Path = Path(file_[-1]) / file_[1]
    if not f_path.is_file():
        return

    dir_id = ag.dir_list.currentIndex().data(Qt.ItemDataRole.UserRole).id
    existent = 0

    file_id = db_ut.registered_file_id(file_[-1], file_[1])
    if file_id:
        existent = db_ut.copy_existent(file_id, dir_id)
    else:
        file_id = db_ut.insert_file(file_)
        db_ut.copy_file(file_id, dir_id)

    db_ut.insert_tags(file_id, fl['tags'])
    db_ut.insert_filenotes(file_id, fl['notes'])
    db_ut.insert_authors(file_id, fl['authors'])
    ag.tag_list.list_changed.emit()
    ag.author_list.list_changed.emit()
    return existent
#endregion

#region  Files - Dirs
def open_manualy(index: QModelIndex):
    btn = ag.show_message_box(
        'File cannot be opened',
        'Please, select file',
        btn=QMessageBox.StandardButton.Open |
        QMessageBox.StandardButton.Cancel,
        icon=QMessageBox.Icon.Question
    )

    if btn == QMessageBox.StandardButton.Cancel:
        return False
    if btn == QMessageBox.StandardButton.Open:
        path = full_file_name(index)
        i_path = Path(path)
        d_path = i_path.parent
        while not d_path.exists():
            d_path = d_path.parent
        filename, ok = QFileDialog.getOpenFileName(ag.app,
            directory=str(d_path)
        )

        if ok:
            f_path = Path(filename)
            path_id = db_ut.get_path_id(f_path.parent.as_posix())
            id = index.data(Qt.ItemDataRole.UserRole).id
            db_ut.update_file_name_path(id, path_id, f_path.name)
            model = ag.file_list.model()
            user_data = model.get_user_data()
            for it in user_data:
                it: ag.FileData
                if it.id == id:
                    it.path = path_id
                    break
            open_with_url(str(f_path))

def create_child_dir():
    cur_idx = ag.dir_list.selectionModel().currentIndex()

    new_idx = insert_dir_row(0, cur_idx)

    if new_idx.isValid():
        create_folder(new_idx)
        ag.dir_list.setExpanded(cur_idx, True)
        ag.dir_list.setCurrentIndex(new_idx)
        ag.dir_list.edit(new_idx)

def insert_dir_row(row: int, parent: QModelIndex) -> QModelIndex:
    model = ag.dir_list.model()
    if not model.insertRow(row, parent):
        return QModelIndex()
    return model.index(row, 0, parent)

def create_dir():
    cur_idx = ag.dir_list.currentIndex()

    new_idx = insert_dir_row(cur_idx.row()+1, cur_idx.parent())

    if new_idx.isValid():
        create_folder(new_idx)
        ag.dir_list.setCurrentIndex(new_idx)
        ag.dir_list.edit(new_idx)

def create_folder(index: QModelIndex):
    """
    finishing creation. Create user data and save in DB
    index: index of created row
    """
    parent = index.parent()
    parent_id = parent.data(Qt.ItemDataRole.UserRole).id if parent.isValid() else 0
    folder_name = "New folder"
    dir_id = db_ut.insert_dir(folder_name, parent_id)

    user_data = ag.DirData(
        parent_id=parent_id,
        id=dir_id,
        is_link=False,
        hidden=False,
        tool_tip=folder_name
    )
    item: dirItem = index.internalPointer()
    item.setUserData(user_data)
    item.setData("New folder", Qt.ItemDataRole.EditRole)

def delete_folders():
    cur_idx = ag.dir_list.currentIndex()
    for idx in ag.dir_list.selectionModel().selectedRows(0):
        u_dat: ag.DirData = idx.data(Qt.ItemDataRole.UserRole)
        if u_dat.is_link:
            db_ut.remove_dir_copy(u_dat.id, u_dat.parent_id)
            continue
        if visited := delete_tree(u_dat):
            delete_visited(visited)
    model: dirModel = ag.dir_list.model()
    near_curr = model.neighbor_idx(cur_idx)
    reload_dirs_changed(near_curr)

def delete_visited(visited: list):
    visited.reverse()
    for dir in visited:
        db_ut.delete_dir(dir.id, dir.parent_id)

def delete_tree(u_dat: ag.DirData, visited=None):
    if visited is None:
        visited = []
    visited.append(u_dat)
    children = db_ut.dir_children(u_dat.id)
    for child in children:
        dir_dat: ag.DirData = ag.DirData(*child)
        if dir_dat.is_link:
            db_ut.remove_dir_copy(dir_dat.id, dir_dat.parent_id)
            continue
        if dir_dat in visited:
            continue
        delete_tree(dir_dat, visited)
    return visited

def reload_dirs_changed(index: QModelIndex, last_id: int=0):
    set_dir_model()
    if index.isValid():
        branch = define_branch(index)
        if last_id:
            branch.append(last_id)
        idx = expand_branch(branch)
        if idx.isValid():
            ag.dir_list.setCurrentIndex(idx)
            ag.dir_list.scrollTo(idx, QAbstractItemView.ScrollHint.PositionAtCenter)

def edit_tooltip():
    cur_idx = ag.dir_list.currentIndex()
    folderEditDelegate.set_tooltip_role()
    ag.dir_list.edit(cur_idx)

def toggle_hidden_state():
    selected = ag.dir_list.selectionModel().selectedIndexes()
    model: dirModel = ag.dir_list.model()
    for idx in selected:
        u_dat: ag.DirData = idx.data(Qt.ItemDataRole.UserRole)
        if u_dat.id:
            u_dat.hidden = not u_dat.hidden
            db_ut.toggle_hidden_dir_state(u_dat.id, u_dat.parent_id, u_dat.hidden)
            item: dirItem = model.getItem(idx)
            item.setUserData(u_dat)
#endregion

#region  Tags
def populate_tag_list():
    ag.tag_list.set_list(db_ut.get_tags())
    sel = ag.get_setting("TAG_SEL_LIST", [])
    ag.tag_list.set_selection(sel)

def tag_selection() -> list:
    return ag.tag_list.get_selected_ids()

def tag_changed(new_tag: str):
    if new_tag == ag.tag_list.get_current():   # edit finished, but tags not changed
        return
    db_ut.update_tag(ag.tag_list.current_id(), new_tag)
    populate_tag_list()
    ag.tag_list.list_changed.emit()

def delete_tags(tags: str):
    """
    tags - comma separated list of tag IDs
    """
    for id in tags.split(','):
        db_ut.detele_tag(id)
    populate_tag_list()
    ag.tag_list.list_changed.emit()
#endregion

def populate_ext_list():
    ag.ext_list.set_list(db_ut.get_ext_list())
    sel = ag.get_setting("EXT_SEL_LIST", [])
    ag.ext_list.set_selection(sel)

def ext_selection() -> list:
    return ag.ext_list.get_selected_ids()

#region  Authors
def populate_author_list():
    ag.author_list.set_list(db_ut.get_authors())
    sel = ag.get_setting("AUTHOR_SEL_LIST", [])
    ag.author_list.set_selection(sel)

def author_selection() -> list:
    return ag.author_list.get_selected_ids()

def author_changed(new_author: str):
    if new_author == ag.author_list.get_current():
        return
    db_ut.update_author(ag.author_list.current_id(), new_author)
    populate_author_list()
    ag.author_list.list_changed.emit()

def delete_authors(authors: str):
    """
    authors - comma separated list of author IDs
    """
    for id in authors.split(','):
        db_ut.detele_author(id)
    populate_author_list()
    ag.author_list.list_changed.emit()
#endregion

def file_notes_show(file_idx: QModelIndex):
    file_id = (
        file_idx.data(Qt.ItemDataRole.UserRole).id
        if file_idx.isValid() else 0
    )
    branch = (
        define_branch(ag.dir_list.currentIndex())
        if ag.mode is ag.appMode.DIR else []
    )
    logger.info(f'{file_id=}, {branch=}')
    ag.file_data.set_data(file_id, branch)
