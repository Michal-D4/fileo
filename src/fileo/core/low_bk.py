import apsw
from collections import defaultdict
from loguru import logger
from pathlib import Path
import pickle

from PyQt6.QtCore import (Qt, QSize, QModelIndex,
    pyqtSlot, QUrl, QDateTime,  QAbstractTableModel,
    )
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import QApplication, QMessageBox, QAbstractItemView

from core import db_ut, app_globals as ag
from core.table_model import TableModel, ProxyModel2
from core.edit_tree_model2 import TreeModel, get_index_path, TreeItem

def exec_user_actions():
    """
    run methods for user_action_signal
    :@param action: string to select handle method
    :@return: None
    """
    data_methods = {
        "Dirs Create folder": create_dir,
        "Dirs Create folder as child": create_child_dir,
        "Dirs Delete folder": delete_folder,
        "Dirs Toggle hidden state": toggle_hidden_state,
        "tag_inserted": populate_tag_list,
        "ext inserted": populate_ext_list,
        "author inserted": populate_author_list,
        "Files Copy full file name": copy_file_name,
        "Files Open file": open_file,
        "double click file": double_click_file,
        "Files Remove file from folder": remove_file,
        "Files Delete file from DB": delete_file,
        "Files Reveal in explorer": open_folder,
        "filter_changed": filter_changed,
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
            print(f'Action not implemented {err}')

    return execute_action

#region Common
def save_settings(**kwargs):
    cursor: apsw.Cursor = ag.db["Conn"].cursor()
    sql = "update settings set value = :value where key = :key;"

    for key, val in kwargs.items():
        cursor.execute(sql, {"key": key, "value": pickle.dumps(val)})

def save_path():
    save_settings(TREE_PATH=current_dir_path())

def get_setting(key: str, default=None):
    cursor: apsw.Cursor = ag.db["Conn"].cursor()
    sql = "select value from settings where key = :key;"

    val = cursor.execute(sql, {"key": key}).fetchone()[0]
    # in case of "TypeError: 'NoneType' object is not subscriptable"
    # execute ("insert into settings (key) values (?), (key,)")
    vv = pickle.loads(val) if val else None

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

def get_id_parent_path(index: QModelIndex):
    item: TreeItem = index.internalPointer()
    path = []
    while 1:
        u_dat = item.user_data()
        path.append(u_dat.id)
        item = item.parent()
        if u_dat.parent_id == 0:
            break
    path.reverse()
    return path

def expand_index_path(id_parent_path: list) -> QModelIndex:
    model = ag.dir_list.model()
    parent = QModelIndex()
    item: TreeItem = model.rootItem
    for it in id_parent_path:
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
    ag.dir_list.selectionModel().selectionChanged.connect(ag.filter.dir_selection_changed)

@pyqtSlot(QModelIndex)
def cur_dir_changed(curr_idx: QModelIndex):
    """
    currentRowChanged signal in dirTree
    :@param curr_idx:
    :@return: None
    """
    if ag.section_resized:   # save column widths if changed
        save_settings(COLUMN_WIDTH=get_columns_width())
        ag.section_resized = False
    if curr_idx.isValid() and ag.mode is ag.appMode.DIR:
        files_from_folder()
        set_current_file(0)

def current_dir_path():
    return get_index_path(ag.dir_list.currentIndex())

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
    row = get_tmp_setting(f"SAVE_ROW{ag.mode.value}", 0)
    save_tmp_settings(**{f"SAVE_ROW{old_mode}": ag.file_list.currentIndex().row()})

    {ag.appMode.DIR: files_from_folder,
     ag.appMode.FILTER: filtered_files,
    } [ag.mode]()
    if ag.file_list.model().rowCount() > 0:
        set_current_file(row)

def populate_file_list():
    if ag.mode is ag.appMode.DIR:
        files_from_folder()
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

def files_from_folder():
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
        model.append_row(ff1, ag.FileData(*ff[-4:]))

    ag.app.ui.others.setText(f"files: {model.rowCount()}")
    if model.rowCount() == 0:
        row = ["THERE ARE NO FILES HERE"]
        for _,typ in field_idx[1:]:
            row.append(field_val(typ))
        model.append_row(row, ag.FileData(-1,0,0,0))

    set_file_model(model)
    header_restore(model)

def set_current_file(row: int):
    idx = ag.file_list.model().index(row, 0)
    if idx.isValid():
        ag.file_list.setCurrentIndex(idx)
        ag.file_list.scrollTo(idx, QAbstractItemView.ScrollHint.PositionAtCenter)

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
    idx = ag.file_list.currentIndex()
    if idx.isValid():
        QApplication.clipboard().setText(full_file_name(idx))

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

def delete_file():
    """
    delete file from DB
    """
    idx = ag.file_list.currentIndex()

    dlg = QMessageBox(ag.app)
    dlg.setWindowTitle('delete file from DB')
    dlg.setText(f'confirm file "{file_name(idx)}" deletion')
    dlg.setStandardButtons(QMessageBox.StandardButton.Ok |
        QMessageBox.StandardButton.Cancel)
    dlg.setIcon(QMessageBox.Icon.Question)
    res = dlg.exec()

    if res == QMessageBox.StandardButton.Ok:
        db_ut.delete_file(idx.data(Qt.ItemDataRole.UserRole).id)
        post_delete_file(idx)

def remove_file():
    """
    remove file from folder
    """
    idx = ag.file_list.currentIndex()
    id = idx.data(Qt.ItemDataRole.UserRole).id

    dir_id = get_dir_id(id)

    if dir_id:
        db_ut.delete_file_dir_link(id, dir_id)
        post_delete_file(idx)

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

def post_delete_file(idx: QModelIndex):
    row = idx.row()
    populate_file_list()
    model = ag.file_list.model()
    if row >= model.rowCount():
        row -= 1
    if row < 0:
        return

    set_current_file(row)
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

    user_data = ag.DirData(dir_id, parent_id, False, False)

    index.internalPointer().setUserData(user_data)

def delete_folder():
    cur_idx = ag.dir_list.selectionModel().currentIndex()
    u_dat: ag.DirData = cur_idx.data(role=Qt.ItemDataRole.UserRole)
    if u_dat.is_copy:
        db_ut.delete_dir_copy(u_dat.id, u_dat.parent_id)
    else:
        db_ut.delete_dir(u_dat.id)

    near_curr = ag.dir_list.model().neighbor_idx(cur_idx)
    reload_dirs_changed(near_curr)

def reload_dirs_changed(index: QModelIndex, last_id: int=0):
    set_dir_model()
    if index.isValid():
        path = get_id_parent_path(index)
        if last_id:
            path.append(last_id)
        idx = expand_index_path(path)
        if idx.isValid():
            ag.dir_list.setCurrentIndex(idx)
            ag.dir_list.selectionModel().selectedRows(idx.row())
            ag.dir_list.scrollTo(idx, QAbstractItemView.ScrollHint.PositionAtCenter)
    ag.dir_list.selectionModel().currentRowChanged.connect(cur_dir_changed)

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

def update_file_tag_links(idx: QModelIndex):
    new_tags = ag.notes.get_selected_tag_ids()
    id = idx.data(Qt.ItemDataRole.UserRole).id
    db_ut.update_file_tag_links(id, new_tags)

def tag_selection() -> list:
    return ag.tag_list.get_selected_ids()

def tag_changed(new_tag: str):
    if new_tag == ag.tag_list.get_current():
        return
    db_ut.update_tag(ag.tag_list.current_id(), new_tag)
    populate_tag_list()

def delete_tags(tags: str):
    """
    tags - comma separated list of tag IDs
    """
    for id in tags.split(','):
        db_ut.detele_tag(id)
    populate_tag_list()
#endregion

#region  Extensions
def populate_ext_list():
    ag.ext_list.set_list(db_ut.get_ext_list())
    sel = get_setting("EXT_SEL_LIST", [])
    ag.ext_list.set_selection(sel)

def _ext_sel_changed():
    """
    there were saving of selected extensions
    really needs insert selected extensions into filter
    """
    pass

def _ext_selection() -> list:
    return ag.ext_list.get_selected_ids()
#endregion

#region  Authors
def populate_author_list():
    ag.author_list.set_list(db_ut.get_authors())
    sel = get_setting("AUTHOR_SEL_LIST", [])
    ag.author_list.set_selection(sel)

def _author_sel_changed():
    """
    there were saving of selected extensions
    really needs insert selected extensions into filter
    """
    pass

def author_selection() -> list:
    return ag.author_list.get_selected_ids()

def author_changed(new_author: str):
    if new_author == ag.author_list.get_current():
        return
    db_ut.update_author(ag.author_list.current_id(), new_author)
    populate_author_list()

def delete_authors(authors: str):
    """
    authors - comma separated list of author IDs
    """
    for id in authors.split(','):
        db_ut.detele_author(id)
    populate_author_list()
#endregion

#region Comments
def file_notes_show(file: QModelIndex):
    f_dat: ag.FileData = file.data(Qt.ItemDataRole.UserRole)
    if f_dat:
        notes = db_ut.get_file_notes(f_dat.id)
        ag.notes.set_notes_data(notes)
        tags = db_ut.get_tags()
        ag.notes.set_tags(tags)
        ag.notes.set_file_id(f_dat.id)
#endregion
