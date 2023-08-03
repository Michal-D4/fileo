from loguru import logger
import apsw
import json
from pathlib import Path
import pickle
import sys
import subprocess

from PyQt6.QtCore import (Qt, QSize, QModelIndex,
    pyqtSlot, QUrl, QDateTime,  QAbstractTableModel,
)
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import (QApplication, QAbstractItemView,
    QFileDialog, QMessageBox,
)

from . import db_ut, app_globals as ag, utils, duplicates as dup
from .table_model import TableModel, ProxyModel2
from .edit_tree_model2 import TreeModel, TreeItem
from ..widgets import about, preferencies

DEFAULT_FIELD_WIDTH = 65

if sys.platform.startswith("win"):
    def reveal_file(path: str):
        # subprocess.run(['explorer.exe', '/select,', os.path.normpath(path)])
        subprocess.run(['explorer.exe', '/select,', path])
elif sys.platform.startswith("linux"):
    def reveal_file(path: str):
        cmd = [
            'dbus-send', '--session', '--dest=org.freedesktop.FileManager1',
            '--type=method_call', '/org/freedesktop/FileManager1',
            'org.freedesktop.FileManager1.ShowItems',
            f'array:string:file:////{path}', 'string:',
        ]
        subprocess.run(cmd)
else:
    def reveal_file(path: str):
        raise NotImplemented(f"doesn't support {sys.platform} system")

def exec_user_actions():
    """
    run methods for user_action_signal
    :@param action: string to select handle method
    :@return: None
    """
    data_methods = {
        "Dirs Create folder": create_dir,
        "Dirs Create folder as child": create_child_dir,
        "Dirs Delete folder(s)": delete_folders,
        "Dirs Toggle hidden state": toggle_hidden_state,
        "Dirs Import files": import_files,
        "tag_inserted": populate_tag_list,
        "ext inserted": populate_ext_list,
        "author_inserted": populate_author_list,
        "Files Copy file name(s)": copy_file_name,
        "Files Copy full file name(s)": copy_full_file_name,
        "Files Open file": open_file,
        "double click file": double_click_file,
        "Files Remove file(s) from folder": remove_files,
        "Files Delete file(s) from DB": delete_files,
        "Files Reveal in explorer": open_folder,
        "Files Rename file": rename_file,
        "Files Export selected files": export_files,
        "filter_changed": filter_changed,
        "Setup About": show_about,
        "Setup Report duplicate files": report_duplicates,
        "Setup Preferencies": set_preferencies,
        "find_files_by_name": find_files_by_name,
        "enable_next_prev": enable_next_prev,
        "Enable_buttons": enable_buttons,
        "reload_dirs": reload_cur_dir,
        "file-note: Go to file": goto_edited_file,
        "remove_file_from_location": remove_file_from_location
      }

    @pyqtSlot(str)
    def execute_action(action: str):
        pos = action.find("/")
        act = action if pos == -1 else action[:pos]
        try:
            if pos == -1:
                data_methods[act]()
            else:
                data_methods[act](action[pos+1:])
        except KeyError as err:
            utils.show_message_box(
                'Action not implemented',
                f'Action name "{err}" not implemented',
                icon=QMessageBox.Icon.Warning
            )

    return execute_action

@pyqtSlot(str)
def goto_edited_file(param: str):
    file_id, branch = param.split('-')
    idx = expand_branch(
        (int(it) for it in branch[1:-1].split(', '))
    )

    if idx.isValid():
        ag.dir_list.setCurrentIndex(idx)
        ag.dir_list.scrollTo(idx, QAbstractItemView.ScrollHint.PositionAtCenter)

        model = ag.file_list.model()
        row = model.get_row_by_id(int(file_id))
        set_current_file(row)

@pyqtSlot()
def report_duplicates():
    rep_creator = dup.Duplicates()
    rep = rep_creator.get_report()
    if rep:
        save_report(rep)
    else:
        utils.show_message_box(
            "No duplicates found",
            "No file duplicates found in DB"
        )

def save_report(rep):
    pp = Path('~/fileo/report').expanduser()
    path = utils.get_app_setting('DEFAULT_REPORT_PATH', pp.as_posix())
    file_name, ok = QFileDialog.getSaveFileName(parent=ag.app,
        caption='Open file to save duplicate files report',
        directory=(Path(path) / 'untitled').as_posix(),
        filter='File list (*.filedups *.txt)'
    )

    if ok:
        _save_report(rep, file_name)

def _save_report(rep: dict[list], filename: str):

    with open(filename, "w") as out:
        for key,rr in rep.items():
            out.write(f"{'-='*20}-\n")
            for r in rr:
                out.write(f"File:  {r[0]}\n")
                out.write(f"  {'; '.join(r[1:])}\n")

@pyqtSlot()
def reload_cur_dir():
    reload_dirs_changed(ag.dir_list.currentIndex())

@pyqtSlot()
def enable_buttons():
    ag.app.ui.btn_search.setEnabled(True)
    ag.app.refresh_tree.setEnabled(True)
    ag.app.show_hidden.setEnabled(True)
    ag.app.collapse_btn.setEnabled(True)

@pyqtSlot()
def rename_file():
    idx = ag.file_list.currentIndex()
    idx0 = ag.file_list.model().index(idx.row(), 0, QModelIndex())
    ag.file_list.setCurrentIndex(idx)
    old_name = full_file_name(idx0)
    ag.file_path = Path(old_name)
    if ag.file_path.exists() and ag.file_path.is_file():
        ag.file_list.edit(idx0)

@pyqtSlot(str)
def rename_in_file_system(new_name: str):
    new_path = ag.file_path.rename(ag.file_path.parent / new_name)
    if new_path.name == new_name:
        ag.app.ui.current_filename.setText(new_name)
    else:
        utils.show_message_box(
            'Error renaming file',
            f'File {ag.file_path.name} was not renamed',
            icon=QMessageBox.Icon.Critical,
            details=ag.file_path.as_posix()
        )

@pyqtSlot()
def enable_next_prev(param: str):
    not_empty = param.split(',')
    ag.app.btn_next.setDisabled(not_empty[0] == 'no')
    ag.app.btn_prev.setDisabled(not_empty[1] == 'no')

@pyqtSlot()
def find_files_by_name(param: str):
    def split3():
        """
        split by commas but into 3 parts
        all pats are merged into one except the 2 last
        """
        pp = param.split(',')
        return ','.join(pp[:-2]), *pp[-2:]

    pp = split3()
    files = db_ut.get_files_by_name(pp[0], int(pp[1]), int(pp[2]))
    show_files(files)

@pyqtSlot()
def set_preferencies():
    pref = preferencies.Preferencies(ag.app)
    pref.show()

@pyqtSlot()
def show_about():
    dlg = about.AboutDialog(ag.app)
    dlg.show()

#region Common
def save_tmp_settings(**kwargs):
    cursor: apsw.Cursor = ag.db["Conn"].cursor()
    sql0 = "delete from aux where key = :key"
    sql1 = "insert into aux values (:key, :value);"

    for key, val in kwargs.items():
        cursor.execute(sql0, {"key": key})
        cursor.execute(sql1, {"key": key, "value": pickle.dumps(val)})

def get_tmp_setting(key: str, default=None):
    cursor: apsw.Cursor = ag.db["Conn"].cursor()
    sql = "select val from aux where key = :key;"

    val = cursor.execute(sql, {"key": key}).fetchone()
    vv = pickle.loads(val[0]) if val else None

    return vv if vv else default

def save_branch_in_temp(index: QModelIndex):
    branch = define_branch(index)
    db_ut.save_branch_in_temp_table(pickle.dumps(branch))

def restore_branch_from_temp() -> QModelIndex:
    val = db_ut.get_branch_from_temp_table()
    return expand_branch(pickle.loads(val) if val else [])

def define_branch(index: QModelIndex) -> list[int]:
    """
    return branch - a list of node ids from root to index
    """
    if not index.isValid():
        return []
    item: TreeItem = index.internalPointer()
    branch = []
    while 1:
        u_dat = item.user_data()
        branch.append(u_dat.id)
        item = item.parent()
        if u_dat.parent_id == 0:
            break
    branch.reverse()
    return branch

def get_dir_names_path(index: QModelIndex) -> list[str]:
    """
    return:  a list of node names from root to index
    """
    if not index.isValid():
        return []
    item: TreeItem = index.internalPointer()
    branch = []
    while 1:
        if not item.parent():
            break
        name = item.data(Qt.ItemDataRole.DisplayRole)
        branch.append(name)
        item = item.parent()
    branch.reverse()
    return branch

def expand_branch(branch: list) -> QModelIndex:
    model = ag.dir_list.model()
    parent = QModelIndex()
    item: TreeItem = model.rootItem
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
    ag.hist_folder = True
    model: TreeModel = TreeModel()
    model.set_model_data()
    ag.dir_list.setModel(model)
    ag.dir_list.setFocus()
    ag.dir_list.selectionModel().selectionChanged.connect(ag.filter_dlg.dir_selection_changed)

    ag.dir_list.setCurrentIndex(QModelIndex())
    ag.dir_list.selectionModel().currentRowChanged.connect(cur_dir_changed)

@pyqtSlot(QModelIndex, QModelIndex)
def cur_dir_changed(curr_idx: QModelIndex, prev_idx: QModelIndex):
    """
    currentRowChanged signal in dirTree
    :@return: None
    """
    def new_history_item():
        if ag.hist_folder:
            ag.hist_folder = False
        else:       # new history item
            add_history_item()
        set_current_file(
            curr_idx.data(Qt.ItemDataRole.UserRole).file_row
        )

    ag.app.ui.folder_path.setText('>'.join(get_dir_names_path(curr_idx)))

    save_columns_width()

    if curr_idx.isValid() and ag.mode is ag.appMode.DIR:
        file_idx = ag.file_list.currentIndex()
        file_row = file_idx.row() if file_idx.isValid() else 0
        save_file_row(file_row, prev_idx)
        show_folder_files()
        new_history_item()

def save_columns_width():
    if ag.section_resized:   # save column widths if changed
        ag.save_settings(COLUMN_WIDTH=get_columns_width())
        ag.section_resized = False

def save_file_row(file_row: int, dir_idx: QModelIndex):
    if dir_idx.isValid():
        u_dat = update_file_row_in_dir_model(file_row, dir_idx)
        db_ut.update_file_row(u_dat)

def update_file_row_in_dir_model(file_row: int, idx: QModelIndex) -> ag.DirData:
        model = ag.dir_list.model()
        dir_item = model.getItem(idx)
        u_data: ag.DirData = dir_item.userData
        u_data.file_row = file_row
        return u_data

def add_history_item():
    ag.history.add_item(
        define_branch(ag.dir_list.currentIndex())
    )

def dir_list_setup():
    ag.dir_list.header().hide()
    icon_size = 12
    indent = 12
    ag.dir_list.setIconSize(QSize(icon_size, icon_size))
    ag.dir_list.setIndentation(indent)
    ag.dir_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
#endregion

#region  Files - setup, populate ...
@pyqtSlot(ag.appMode)
def app_mode_changed(old_mode: ag.appMode):
    if ag.mode is ag.appMode.FILTER_SETUP:
        return
    if not ag.db['Conn']:
        return
    row = get_tmp_setting(f"SAVE_ROW{ag.mode.value}", 0)
    save_tmp_settings(**{f"SAVE_ROW{old_mode}": ag.file_list.currentIndex().row()})

    refresh_file_list()
    if ag.file_list.model().rowCount() > 0:
        set_current_file(row)

def refresh_file_list():
    if ag.mode is ag.appMode.DIR:
        show_folder_files()
    else:
        filtered_files()

def populate_file_list():
    if ag.mode is ag.appMode.DIR:
        ag.hist_folder = True
        _history_folder(ag.history.get_current())
    else:             # appMode.FILTER or appMode.FILTER_SETUP
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
    ag.hist_folder = True
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
    files = ag.filter_dlg.get_file_list()
    show_files(files)

def filter_changed():
    filtered_files()
    set_current_file(0)

def show_folder_files():
    idx = ag.dir_list.currentIndex()
    u_dat: ag.DirData = idx.data(Qt.ItemDataRole.UserRole)

    files = db_ut.get_files(u_dat.id, u_dat.parent_id) if u_dat else []
    show_files(files)

def show_files(files):
    """
    populate file's model
    :@param files
    """
    model = fill_file_model(files)
    set_file_model(model)
    header_restore(model)
    model.model_data_changed.connect(rename_in_file_system)

def fill_file_model(files) -> TableModel:
    model: TableModel = TableModel()
    field_idx = field_indexes()

    for ff in files:
        ff1 = []
        for i,typ in field_idx:
            ff1.append(field_val(typ, ff[i]))
        model.append_row(ff1, ag.FileData(*ff[-3:]))

    rows = model.rowCount()
    ag.app.ui.file_count.setText(f"files: {rows}")

    if rows == 0:
        row = ["THERE ARE NO FILES HERE"]
        for _,typ in field_idx[1:]:
            row.append(field_val(typ))
        model.append_row(row, ag.FileData(-1,0,0))

    return model

def set_current_file(row: int):
    idx = ag.file_list.model().index(row, 0)
    if idx.isValid():
        ag.file_list.setCurrentIndex(idx)
        ag.file_list.scrollTo(
            idx, QAbstractItemView.ScrollHint.PositionAtCenter
        )

def field_val(typ:str, val=0):
    if typ == "str":
        return val
    if typ == "int":
        return int(val)
    a = QDateTime()
    a.setSecsSinceEpoch(val)
    return a

def field_indexes() -> list:
    field_types = (
        'str', 'date', 'int', 'int', 'date',
        'int', 'int', 'date', 'date', 'date',
    )
    acts = ag.field_menu.menu().actions()
    af_no = []
    for i,a in enumerate(acts):
        if a.isChecked():
            af_no.append((i, field_types[i]))

    return af_no

def set_file_model(model: TableModel):
    proxy_model = ProxyModel2()
    proxy_model.setSourceModel(model)
    proxy_model.setSortCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
    model.setHeaderData(0, Qt.Orientation.Horizontal, field_titles())
    ag.file_list.setModel(proxy_model)

def header_restore(model: QAbstractTableModel):
    hdr = field_titles()
    model.setHeaderData(0, Qt.Orientation.Horizontal, hdr)
    width = ag.get_setting("COLUMN_WIDTH", {})

    for i,field in enumerate(hdr):
        ww = width[field] or DEFAULT_FIELD_WIDTH
        ag.file_list.setColumnWidth(i, int(ww))
    ag.file_list.header().sectionResized.connect(section_resized)

def section_resized(idx: int, old_sz: int, new_sz: int):
    ag.section_resized = True

def get_columns_width() -> dict[int]:
    hdr = field_titles()
    logger.info(hdr)

    width = ag.get_setting("COLUMN_WIDTH", {})
    logger.info(width)
    for i,field in enumerate(hdr):
        width[field] = ag.file_list.columnWidth(i)
    logger.info(width)
    return width

def field_titles() -> list:
    acts = ag.field_menu.menu().actions()
    return [a.text() for a in acts if a.isChecked()]

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
        reveal_file(path)

def full_file_name(index: QModelIndex) -> str:
    path_id = index.data(Qt.ItemDataRole.UserRole).path
    path = db_ut.get_file_path(path_id)
    name = file_name(index)
    return str(Path(path) / name) if name else ''

def file_name(index: QModelIndex) -> str:
    if index.column():
        index = ag.file_list.model().index(index.row(), 0)
    return index.data(Qt.ItemDataRole.DisplayRole)

def double_click_file():
    idx = ag.file_list.currentIndex()
    if idx.isValid() and (idx.column() == 0):
        open_file0(idx)

def open_file():
    idx = ag.file_list.currentIndex()
    if idx.isValid():
        open_file0(idx)

def open_file0(index: QModelIndex):
    if open_file_or_folder(full_file_name(index)):
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

    res = utils.show_message_box(
        'delete file from DB',
        f'Selected files will be deleted. Please confirm',
        QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel,
        QMessageBox.Icon.Question
    )

    if res == QMessageBox.StandardButton.Ok:
        row = ag.file_list.model().rowCount()
        for idx in ag.file_list.selectionModel().selectedRows(0):
            row = min(row, idx.row())
            db_ut.delete_file(idx.data(Qt.ItemDataRole.UserRole).id)
        post_delete_file(row)

def remove_files():
    row = ag.file_list.model().rowCount()
    for idx in ag.file_list.selectionModel().selectedRows(0):
        row = min(row, idx.row())
        id = idx.data(Qt.ItemDataRole.UserRole).id
        dir_id = get_dir_id(id)
        db_ut.delete_file_dir_link(id, dir_id)
    post_delete_file(row)

def remove_file_from_location(param: str):
    dir_id, id = param.split(',')
    db_ut.delete_file_dir_link(id, dir_id)
    ag.file_data_holder.set_file_id(int(id))

def get_dir_id(file: int) -> int:
    """
    in case of appMode.DIR - returns id of current folder
    otherwise - returns id of arbitrary folder contained current file
    """
    if ag.mode is ag.appMode.DIR:
        dir_idx = ag.dir_list.currentIndex()
        dir_dat: ag.DirData = dir_idx.data(Qt.ItemDataRole.UserRole)
        return dir_dat.id

    return db_ut.get_dir_id_for_file(file)

def post_delete_file(row: int):
    populate_file_list()
    model = ag.file_list.model()
    row -= int(row >= model.rowCount())

    set_current_file(row)
#endregion

#region  export-import
def export_files():
    pp = Path('~/fileo/export').expanduser()
    path = utils.get_app_setting('DEFAULT_EXPORT_PATH', pp.as_posix())
    file_name, ok = QFileDialog.getSaveFileName(parent=ag.app,
        caption='Open file to save list of exported files',
        directory=(Path(path) / 'untitled').as_posix(),
        filter='File list (*.file_list *.json *.txt)'
    )

    if ok:
        _export_files(file_name)

def _export_files(filename: str):
    with open(filename, "w") as out:
        res = []
        for idx in ag.file_list.selectionModel().selectedRows(0):
            try:
                id = idx.data(Qt.ItemDataRole.UserRole).id
                file_data = db_ut.get_export_data(idx.data(Qt.ItemDataRole.UserRole).id)
            except TypeError:
                continue
            out.write(f"{json.dumps(file_data)}\n")

def import_files():
    pp = Path('~/fileo/export').expanduser()
    path = utils.get_app_setting('DEFAULT_EXPORT_PATH', pp.as_posix())
    file_name, ok = QFileDialog.getOpenFileName(ag.app,
        caption="Open file to import list of files",
        directory=path,
        filter="File list (*.file_list *.json *.txt)")
    if ok:
        _import_files(file_name)

def _import_files(filename):
    branch = define_branch(ag.dir_list.currentIndex())
    exist_dir = 0

    with open(filename, "r") as fp:
        for line in fp:
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
    existed = 0

    id = db_ut.registered_file_id(file_[-1], file_[1])
    if id:
        existed = db_ut.copy_existed(id, dir_id)
    else:
        id = db_ut.insert_file(file_)
        db_ut.copy_file(id, dir_id)

    db_ut.insert_tags(id, fl['tags'])
    db_ut.insert_filenotes(id, fl['notes'])
    db_ut.insert_authors(id, fl['authors'])
    return existed
#endregion

#region  Files - Dirs
def open_file_or_folder(path: str) -> bool:
    """
    Open file with default programm
    or folder with default file manager
    @param: path
    """
    url = QUrl()
    return QDesktopServices.openUrl(url.fromLocalFile(path))

def create_child_dir():
    cur_idx = ag.dir_list.selectionModel().currentIndex()

    new_idx = insert_dir_row(0, cur_idx)

    if new_idx.isValid():
        create_folder(new_idx)
        ag.dir_list.setExpanded(cur_idx, True)
        ag.dir_list.setCurrentIndex(new_idx)

def insert_dir_row(row: int, parent: QModelIndex) -> QModelIndex:
    model = ag.dir_list.model()
    if not model.insertRow(row, parent):
        return QModelIndex()

    index = model.index(row, 0, parent)
    model.setData(index, "New folder", Qt.ItemDataRole.EditRole)

    return index

def create_dir():
    cur_idx = ag.dir_list.currentIndex()

    new_idx = insert_dir_row(cur_idx.row()+1, cur_idx.parent())

    if new_idx.isValid():
        create_folder(new_idx)
        ag.dir_list.setCurrentIndex(new_idx)

def create_folder(index: QModelIndex):
    """
    finishing creation. Create user data and save in DB
    index: index of created row
    """
    parent = index.parent()
    parent_id = parent.data(Qt.ItemDataRole.UserRole).id if parent.isValid() else 0

    folder_name = "New folder"
    dir_id = db_ut.insert_dir(folder_name, parent_id)

    user_data = ag.DirData(parent_id, dir_id, False, False)

    index.internalPointer().setUserData(user_data)

def delete_folders():
    cur_idx = ag.dir_list.currentIndex()
    for idx in ag.dir_list.selectionModel().selectedRows(0):
        u_dat: ag.DirData = idx.data(Qt.ItemDataRole.UserRole)
        if u_dat.is_link:
            db_ut.remove_dir_copy(u_dat.id, u_dat.parent_id)
            continue
        if visited := delete_tree(u_dat):
            delete_visited(visited)
    near_curr = ag.dir_list.model().neighbor_idx(cur_idx)
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

def toggle_hidden_state():
    selected = ag.dir_list.selectionModel().selectedIndexes()
    model: TreeModel = ag.dir_list.model()
    for idx in selected:
        u_dat: ag.DirData = idx.data(Qt.ItemDataRole.UserRole)
        if u_dat:
            u_dat.hidden = not u_dat.hidden
            db_ut.toggle_hidden_dir_state(u_dat.id, u_dat.parent_id, u_dat.hidden)
            item: TreeItem = model.getItem(idx)
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
    if new_tag == ag.tag_list.get_current():
        # edit finished, but tag wasn't changed
        return
    db_ut.update_tag(ag.tag_list.current_id(), new_tag)
    populate_tag_list()
    ag.tag_list.edit_finished.emit()

def delete_tags(tags: str):
    """
    tags - comma separated list of tag IDs
    """
    for id in tags.split(','):
        db_ut.detele_tag(id)
    populate_tag_list()
    ag.tag_list.edit_finished.emit()
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
    ag.author_list.edit_finished.emit()

def delete_authors(authors: str):
    """
    authors - comma separated list of author IDs
    """
    for id in authors.split(','):
        db_ut.detele_author(id)
    populate_author_list()
    ag.author_list.edit_finished.emit()
#endregion

def file_notes_show(file: QModelIndex):
    f_dat: ag.FileData = file.data(Qt.ItemDataRole.UserRole)
    if f_dat:
        ag.file_data_holder.set_branch(
            define_branch(ag.dir_list.currentIndex())
        )
        ag.file_data_holder.set_file_id(f_dat.id)
