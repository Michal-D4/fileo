import apsw
from collections import defaultdict
import json
from loguru import logger
from pathlib import Path
import pickle

from PyQt6.QtCore import (Qt, QSize, QModelIndex,
    pyqtSlot, QUrl, QDateTime,  QAbstractTableModel,
)
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import (QApplication, QAbstractItemView,
    QFileDialog, QMessageBox,
)

from . import db_ut, app_globals as ag, utils
from .table_model import TableModel, ProxyModel2
from .edit_tree_model2 import TreeModel, TreeItem
from ..widgets import about, preferencies

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
        "author inserted": populate_author_list,
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
        "Setup Preferencies": set_preferencies,
        "find_files_by_name": find_files_by_name,
        "enable_next_prev": enable_next_prev,
        "Enable_buttons": enable_buttons,
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
            dlg = QMessageBox(ag.app)
            dlg.setWindowTitle('Action not implemented')
            dlg.setText(f'Action name "{err}" not implemented')
            dlg.setStandardButtons(QMessageBox.StandardButton.Close)
            dlg.setIcon(QMessageBox.Icon.Warning)
            dlg.exec()

    return execute_action

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
        dlg = QMessageBox(ag.app)
        dlg.setWindowTitle('Error renaming file')
        dlg.setText(f'File {ag.file_path.name} was not renamed')
        dlg.setDetailedText(ag.file_path.as_posix())
        dlg.setStandardButtons(QMessageBox.StandardButton.Close)
        dlg.setIcon(QMessageBox.Icon.Critical)
        dlg.exec()

@pyqtSlot()
def enable_next_prev(param: str):
    not_empty = param.split(',')
    ag.app.btn_next.setDisabled(not_empty[0] == 'no')
    ag.app.btn_prev.setDisabled(not_empty[1] == 'no')

@pyqtSlot()
def find_files_by_name(param: str):
    pp = param.split(',')
    files = db_ut.get_files_by_name(pp[0], int(pp[1]), int(pp[2]))
    show_files(files)

@pyqtSlot()
def set_preferencies():
    pref = preferencies.Preferencies(ag.app)
    pref.resize(499, 184)
    pref.show()

@pyqtSlot()
def show_about():
    dlg = about.AboutDialog(ag.app)
    dlg.show()

#region Common
def save_settings(**kwargs):
    """
    used to save settings on DB level
    """
    if not ag.db["Conn"]:
        return
    cursor: apsw.Cursor = ag.db["Conn"].cursor()
    sql = "update settings set value = :value where key = :key;"

    for key, val in kwargs.items():
        cursor.execute(sql, {"key": key, "value": pickle.dumps(val)})

def get_setting(key: str, default=None):
    """
    used to restore settings on DB level
    """
    if not ag.db["Conn"]:
        return default
    cursor: apsw.Cursor = ag.db["Conn"].cursor()
    sql = "select value from settings where key = :key;"

    val = cursor.execute(sql, {"key": key}).fetchone()[0]
    try:
        vv = pickle.loads(val) if val else None
    except:
        vv = default
    # logger.info(f'{key=}, {vv=}')

    return vv if vv else default

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

def save_branch():
    save_settings(TREE_PATH=get_branch(ag.dir_list.currentIndex()))

def restore_branch() -> QModelIndex:
    return expand_branch(get_setting('TREE_PATH', []))

def save_branch_in_temp(index: QModelIndex):
    branch = get_branch(index)
    db_ut.save_branch_in_temp(pickle.dumps(branch))

def restore_branch_from_temp() -> QModelIndex:
    val = db_ut.get_branch_from_temp()
    return expand_branch(pickle.loads(val) if val else [])

def get_branch(index: QModelIndex) -> list[int]:
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
            parent = QModelIndex()
            break

    return parent
#endregion

#region  Dirs
def set_dir_model():
    model: TreeModel = TreeModel()
    model.set_model_data()
    ag.dir_list.setModel(model)
    ag.dir_list.setFocus()
    ag.dir_list.selectionModel().selectionChanged.connect(ag.filter.dir_selection_changed)

@pyqtSlot(QModelIndex, QModelIndex)
def cur_dir_changed(curr_idx: QModelIndex, prev_idx: QModelIndex):
    """
    currentRowChanged signal in dirTree
    :@param curr_idx:
    :@return: None
    """
    def set_history():
        if ag.hist_folder:
            ag.hist_folder = False
        else:       # new history item
            add_history_item(file_row)
            save_file_row_in_model(file_row, prev_idx)
            ag.file_row = curr_idx.data(Qt.ItemDataRole.UserRole).file_row

    ag.app.ui.folder_path.setText('>'.join(get_dir_names_path(curr_idx)))
    if ag.section_resized:   # save column widths if changed
        save_settings(COLUMN_WIDTH=get_columns_width())
        ag.section_resized = False
    if curr_idx.isValid() and ag.mode is ag.appMode.DIR:
        file_idx = ag.file_list.currentIndex()
        file_row = file_idx.row() if file_idx.isValid() else 0
        show_folder_files()
        # logger.info(f'{ag.hist_folder=}, {file_row=}')
        set_history()
        set_current_file(ag.file_row)

def save_file_row_in_model(file_row: int, prev_idx: QModelIndex):
    model = ag.dir_list.model()
    dir_item = model.getItem(prev_idx)
    dir_item.userData.file_row = file_row

def add_history_item(file_row: int):
    ag.history.set_file_id(file_row)
    branch = get_branch(ag.dir_list.currentIndex())
    ag.history.add_item(branch, 0)

def current_dir_path():
    return get_branch(ag.dir_list.currentIndex())

def restore_path(path: list) -> QModelIndex:
    """
    restore expand state and current index of dir_list
    :return: current index
    """
    model: TreeModel = ag.dir_list.model()
    parent = QModelIndex()

    try:
        for id in path:
            if parent.isValid():
                if not ag.dir_list.isExpanded(parent):
                    ag.dir_list.setExpanded(parent, True)
            parent = model.index(int(id), 0, parent)
    except IndexError:
        if model.rowCount(QModelIndex()) > 0:
            parent = model.index(0, 0, QModelIndex())

    ag.dir_list.setCurrentIndex(parent)
    ag.dir_list.scrollTo(parent, QAbstractItemView.ScrollHint.PositionAtCenter)
    return parent

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

    {ag.appMode.DIR: show_folder_files,
     ag.appMode.FILTER: filtered_files,
    } [ag.mode]()
    if ag.file_list.model().rowCount() > 0:
        set_current_file(row)

def populate_file_list():
    if ag.mode is ag.appMode.DIR:
        show_folder_files()
    else:             # appMode.FILTER or appMode.FILTER_SETUP
        filtered_files()

def filtered_files():
    """
    create a list of files by filter
    """
    files = ag.filter.get_file_list()
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
    model: TableModel = TableModel()
    field_idx = field_indexes()

    for ff in files:
        ff1 = []
        for i,typ in field_idx:
            ff1.append(field_val(typ, ff[i]))
        model.append_row(ff1, ag.FileData(*ff[-3:]))

    ag.app.ui.file_count.setText(f"files: {model.rowCount()}")

    if model.rowCount() == 0:
        row = ["THERE ARE NO FILES HERE"]
        for _,typ in field_idx[1:]:
            row.append(field_val(typ))
        model.append_row(row, ag.FileData(-1,0,0))

    set_file_model(model)
    header_restore(model)
    model.model_data_changed.connect(rename_in_file_system)

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
    field_types = ('str', 'date', 'int', 'int', 'date',
                'int', 'int', 'date', 'date', 'date',)
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
    ww = get_setting("COLUMN_WIDTH", {})
    width = defaultdict(lambda: 100, ww)

    for i,field in enumerate(hdr):
        ww = width[field]
        ag.file_list.setColumnWidth(i, int(ww))
    ag.file_list.header().sectionResized.connect(section_resized)

def section_resized(idx: int, old_sz: int, new_sz: int):
    ag.section_resized = True

def get_columns_width() -> dict[int]:
    hdr = field_titles()
    width = get_setting("COLUMN_WIDTH", {})
    for i,field in enumerate(hdr):
        width[field] = ag.file_list.columnWidth(i)
    return width

def field_titles() -> list:
    acts = ag.field_menu.menu().actions()
    af_name = []
    for i,a in enumerate(acts):
        if a.isChecked():
            af_name.append(a.text())

    return af_name

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
        path_id = idx.data(Qt.ItemDataRole.UserRole).path
        path = db_ut.get_file_path(path_id)
        open_file_or_folder(path)

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

    dlg = QMessageBox(ag.app)
    dlg.setWindowTitle('delete file from DB')
    dlg.setText(f'Selected files will be deleted. Please confirm')
    dlg.setStandardButtons(QMessageBox.StandardButton.Ok |
        QMessageBox.StandardButton.Cancel)
    dlg.setIcon(QMessageBox.Icon.Question)
    res = dlg.exec()

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
    branch = get_branch(ag.dir_list.currentIndex())
    exist_dir = 0

    with open(filename, "r") as fp:
        for line in fp:
            exist_dir = load_file(json.loads(line))

    if exist_dir > 0:
        branch.append(exist_dir)
        set_dir_model()
        idx = expand_branch(branch)
        ag.dir_list.selectionModel().currentRowChanged.connect(cur_dir_changed)
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
    db_ut.insert_comments(id, fl['comments'])
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
        if u_dat.is_copy:
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
        if dir_dat.is_copy:
            db_ut.remove_dir_copy(dir_dat.id, dir_dat.parent_id)
            continue
        if dir_dat in visited:
            continue
        delete_tree(dir_dat, visited)
    return visited

def reload_dirs_changed(index: QModelIndex, last_id: int=0):
    set_dir_model()
    ag.dir_list.selectionModel().currentRowChanged.connect(cur_dir_changed)
    if index.isValid():
        branch = get_branch(index)
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
    sel = get_setting("TAG_SEL_LIST", [])
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
    sel = get_setting("EXT_SEL_LIST", [])
    ag.ext_list.set_selection(sel)

def ext_selection() -> list:
    return ag.ext_list.get_selected_ids()

#region  Authors
def populate_author_list():
    ag.author_list.set_list(db_ut.get_authors())
    sel = get_setting("AUTHOR_SEL_LIST", [])
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
        ag.notes.set_notes_data(db_ut.get_file_notes(f_dat.id))
        ag.notes.set_file_id(f_dat.id)
