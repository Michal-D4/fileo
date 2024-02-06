from loguru import logger
import apsw
import json
from pathlib import Path
import pickle
import datetime

from PyQt6.QtCore import (Qt, QSize, QModelIndex,
    pyqtSlot, QUrl, QDateTime, QFile, QTextStream,
    QIODeviceBase,
)
from PyQt6.QtGui import QDesktopServices, QAction, QFocusEvent
from PyQt6.QtWidgets import (QApplication, QAbstractItemView,
    QFileDialog, QMessageBox, QMenu,
)

from . import (db_ut, app_globals as ag, reports as rep, check_update as upd,
)
from .file_model import fileModel, fileProxyModel
from .dir_model import dirModel, dirItem
from ..widgets import about, preferences
from ..widgets.open_db import OpenDB
from ..widgets.scan_disk_for_files import diskScanner
from src import tug

MAX_WIDTH_DB_DIALOG = 300

hist_folder: bool = True
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


def set_user_actions_handler():
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
        "Files Open file": open_current_file,
        "double click file": double_click_file,
        "Files Remove file(s) from folder": remove_files,
        "Files Delete file(s) from DB": delete_files,
        "Files Reveal in explorer": open_folder,
        "Files Rename file": rename_file,
        "Files Export selected files": export_files,
        "filter_changed": filter_changed,
        "MainMenu New window": new_window,
        "MainMenu Create/Open DB": create_open_db,
        "MainMenu Select DB from list": show_db_list,
        "MainMenu Scan disk for files": scan_disk,
        "MainMenu About": show_about,
        "MainMenu Report duplicate files": report_duplicates,
        "MainMenu Report files with same names": report_same_names,
        "MainMenu Preferences": set_preferences,
        "MainMenu Check for update": upd.check4update,
        "find_files_by_name": find_files_by_name,
        "enable_next_prev": enable_next_prev,
        "Enable_buttons": enable_buttons,
        "file-note: Go to file": goto_edited_file,
        "remove_file_from_location": remove_file_from_location,
        "SaveEditState": save_note_edit_state,
        "show file": single_file,
        "file reveal": reveal_in_explorer,
        "Files Clear file history": clear_file_history,
        "Files Remove selected from history": remove_selected_from_history,
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

def clear_file_history():
    ag.file_history.clear()
    ag.switch_first_mode()

def remove_selected_from_history():
    for idx in ag.file_list.selectionModel().selectedRows(0):
        ag.file_history.remove(idx.data(Qt.ItemDataRole.UserRole).id)
    show_recent_files()

def save_db_list():
    if tug.open_db:
        tug.open_db.close()
    else:
        db_open = OpenDB(ag.app)
        db_open.close()

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
    if tug.open_db:
        tug.open_db.close()
    db_open = OpenDB(ag.app)
    db_open.add_db()

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
        NOTE_EDIT_STATE=ag.file_data_holder.get_edit_state()
    )

def new_window(db_name: str=''):
    import subprocess
    import sys
    # logger.info(f'{db_name=}, frozen: {getattr(sys, "frozen", False)}')
    if getattr(sys, "frozen", False):
        # logger.info(f'1) {db_name=}, {ag.entry_point}')
        subprocess.Popen([ag.entry_point, db_name, ])
    else:
        # logger.info(f'2) {db_name=}, {ag.entry_point}')
        subprocess.Popen(
            [sys.executable, ag.entry_point, db_name, ], # sys.executable - python interpreter
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
    """
    new_mode - a key of checkable_btn dict
    """
    # logger.info(f'{ag.mode=!r}, {ag.first_mode=!r}, {new_mode=!r}')
    checkable_btn = {
        ag.appMode.DIR: ag.app.ui.btnDir,
        ag.appMode.FILTER: ag.app.ui.btnFilter,
        ag.appMode.FILTER_SETUP: ag.app.ui.btnFilterSetup,
    }

    # need loop to find button to upcheck
    for key, btn in checkable_btn.items():
        btn.setIcon(tug.get_icon(btn.objectName(), int(key is new_mode)))

    checkable_btn[new_mode].setChecked(True)
    ag.set_mode(new_mode)

def report_duplicates():
    rep_creator = rep.Duplicates()
    repo = rep_creator.get_report()
    if repo:
        save_dup_report(repo)
    else:
        ag.show_message_box(
            "No duplicates found",
            "No file duplicates found in DB"
        )

def report_same_names():
    rep_creator = rep.sameFileNames()
    repo = rep_creator.get_report()
    if repo:
        save_same_names_report(repo)
    else:
        ag.show_message_box(
            "No duplicates found",
            "No file duplicates found in DB"
        )

def save_same_names_report(rep: list):
    file_name, ok = create_report_file()
    if ok:
        with open(file_name, "w") as out:
            out.write(f'DB path: {ag.db.path}\n')
            out.write(
                'each line contains:\n    '
                'file name, path, folder, modification date\n'
            )
            for rr in rep:
                out.write(f"{'-='*20}-\n")
                for r in rr:
                    ts = datetime.datetime.fromtimestamp(r[-1])
                    out.write(
                        f'{".".join(r[:2])}, {r[2]}, {r[3]}, '
                        f'{ts.strftime("%Y-%m-%d %H:%M:%S")}\n'
                    )

def create_report_file() -> tuple:
    pp = Path('~/fileo/report').expanduser()
    path = tug.get_app_setting('DEFAULT_REPORT_PATH', pp.as_posix())
    return QFileDialog.getSaveFileName(parent=ag.app,
        caption='Open file to save report',
        directory=(Path(path) / 'untitled').as_posix(),
        filter='File list (*.report *.txt)'
    )

def save_dup_report(rep: dict):
    file_name, ok = create_report_file()
    if ok:
        with open(file_name, "w") as out:
            out.write(f'DB path: {ag.db.path}\n')
            for key,rr in rep.items():
                out.write(f"{'-='*20}-\n")
                for r in rr:
                    out.write(f"File:  {r[0]}\n")
                    out.write(f"  {'; '.join(r[1:])}\n")

def enable_buttons():
    ag.app.ui.btn_search.setEnabled(True)
    ag.app.refresh_tree.setEnabled(True)
    ag.app.show_hidden.setEnabled(True)
    ag.app.collapse_btn.setEnabled(True)

def rename_file():
    idx: QModelIndex = ag.file_list.currentIndex()
    logger.info(f'{idx.column()=}')
    idx = ag.file_list.model().index(idx.row(), 0)
    ag.file_list.setCurrentIndex(idx)
    ag.file_list.edit(idx)

def enable_next_prev(param: str):
    not_empty = param.split(',')
    ag.app.btn_next.setDisabled(not_empty[0] == 'no')
    ag.app.btn_prev.setDisabled(not_empty[1] == 'no')

def find_files_by_name(param: str):
    def split3():
        """
        split by commas but into 3 parts
        all pats are merged into one except the 2 last
        """
        pp = param.split(',')
        return ','.join(pp[:-2]), *pp[-2:]

    pp = split3()
    srch_line, *_ = ag.get_setting('SEARCH_FILE', ('',0,0))
    ag.app.ui.files_heading.setText(f'Found files "{srch_line}"')
    files = db_ut.get_files_by_name(pp[0], int(pp[1]), int(pp[2]))
    ag.set_mode(ag.appMode.FOUND_FILES)

    show_files(files)
    ag.file_list.setFocus()

def set_preferences():
    pref = preferences.Preferences(ag.app)
    pref.show()

def show_about():
    dlg = about.AboutDialog(ag.app)
    dlg.show()

#region Common
def save_tmp_settings(**kwargs):
    cursor: apsw.Cursor = ag.db.conn.cursor()
    sql0 = "delete from aux where key = :key"
    sql1 = "insert into aux values (:key, :value);"

    for key, val in kwargs.items():
        cursor.execute(sql0, {"key": key})
        cursor.execute(sql1, {"key": key, "value": pickle.dumps(val)})

def get_tmp_setting(key: str, default=None):
    cursor: apsw.Cursor = ag.db.conn.cursor()
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
        name = item.data(Qt.ItemDataRole.DisplayRole)
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

@pyqtSlot(QModelIndex, QModelIndex)
def cur_dir_changed(curr_idx: QModelIndex, prev_idx: QModelIndex):
    """
    currentRowChanged signal in dirTree
    :@return: None
    """
    def set_folder_path_label(idx: QModelIndex):
        if idx.isValid():
            ag.app.ui.folder_path.setText('>'.join(get_dir_names_path(idx)))

    ag.app.collapse_btn.setChecked(False)
    set_folder_path_label(curr_idx)

    if curr_idx.isValid() and ag.mode is ag.appMode.DIR:
        def new_history_item():
            global hist_folder
            if hist_folder:
                hist_folder = False
            else:       # new history item
                add_history_item()

        save_file_id(prev_idx)
        show_folder_files()
        new_history_item()

def dirlist_get_focus(e: QFocusEvent):
    if e.reason() is Qt.FocusReason.ActiveWindowFocusReason:
        return
    ag.switch_first_mode()

def save_file_id(dir_idx: QModelIndex):
    if dir_idx.isValid():
        file_idx = ag.file_list.currentIndex()
        file_id = file_idx.data(Qt.ItemDataRole.UserRole).id
        u_dat = update_file_id_in_dir_model(file_id, dir_idx)

        db_ut.update_file_id(u_dat)

def update_file_id_in_dir_model(file_id: int, idx: QModelIndex) -> ag.DirData:
        model = ag.dir_list.model()
        dir_item = model.getItem(idx)
        u_data: ag.DirData = dir_item.userData
        u_data.file_id = file_id
        return u_data

def add_history_item():
    ag.history.add_item(
        define_branch(ag.dir_list.currentIndex())
    )

def dir_dree_view_setup():
    ag.dir_list.header().hide()
    icon_size = 12
    indent = 12
    ag.dir_list.setIconSize(QSize(icon_size, icon_size))
    ag.dir_list.setIndentation(indent)
    ag.dir_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
#endregion

#region  Files - setup, populate ...
def set_field_menu():
    hdr = ag.file_list.header()

    menu = QMenu(ag.app)
    for i,field,tt in zip(range(len(fields)), fields, tool_tips):
        act = QAction(field, ag.app, checkable=True)
        if tt:
            act.setToolTip(tt)
        act.setChecked(int(not hdr.isSectionHidden(i)))
        act.triggered.connect(lambda state, idx=i: toggle_show_column(state, index=idx))
        menu.addAction(act)

    menu.actions()[0].setEnabled(False)
    menu.setToolTipsVisible(True)
    ag.app.ui.field_menu.setMenu(menu)

def toggle_show_column(state: bool, index: int):
    ag.file_list.header().setSectionHidden(index, not state)
    ag.signals_.toggle_column.emit()

@pyqtSlot(ag.appMode)
def app_mode_changed(prev_mode: int):
    prev = ag.appMode(prev_mode)

    if not ag.db.conn:
        return
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
    global hist_folder
    if not branch:
        return
    hist_folder = True
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

def filter_changed():
    ag.set_mode(ag.appMode.FILTER)
    filtered_files()

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
    ag.app.ui.files_heading.setText(f'Recent files')
    files = get_recent_files()

    show_files(files)
    ag.file_list.setFocus()

def get_recent_files() -> list:
    ''' in LIFO order '''
    ag.set_mode(ag.appMode.HISTORY_FILES)
    return (db_ut.get_file(id_) for id_ in ag.file_history[::-1])

def show_files(files, file_id: int = 0):
    """
    populate file's model
    :@param files
    :@param file_id - if 0 no file was selected
    """
    ag.file_list.setSortingEnabled(
        ag.mode is not ag.appMode.HISTORY_FILES
    )
    model = fill_file_model(files)
    set_file_model(model)

    set_current_file(file_id)

def single_file(file_id: str):
    if ag.mode is ag.appMode.DIR:
        save_file_id(ag.dir_list.currentIndex())
    elif ag.mode is ag.appMode.FILTER:
        ag.save_settings(
            FILTER_FILE_ROW=ag.file_list.currentIndex().row()
        )
    ag.set_mode(ag.appMode.FILE_BY_REF)
    ag.app.ui.files_heading.setText('note referenced file')

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
            (filename.stem, filename.suffix)
            if filename.suffix else
            (filename.stem,)
        )
        model.append_row(ff1, ag.FileData(*ff[-3:]))

    rows = model.rowCount()
    ag.app.ui.file_count.setText(f"files: {rows}")

    if rows == 0:
        null_file_list(model)
    return model

def null_file_list(model: fileModel):
    row = ["NO FILES HERE"]
    for _,typ in enumerate(field_types[1:]):
        row.append(field_val(typ))
    model.append_row(row)

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
    proxy_model.setSortCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
    proxy_model.setSortRole(Qt.ItemDataRole.UserRole+1)
    model.setHeaderData(0, Qt.Orientation.Horizontal, fields)
    ag.file_list.setModel(proxy_model)

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
        ag.add_history_file(idx.data(Qt.ItemDataRole.UserRole).id)

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
    if open_with_url(full_file_name(index)):
        update_open_date(index)
    else:
        open_manualy(index)
    ag.add_history_file(index.data(Qt.ItemDataRole.UserRole).id)

def open_with_url(path: str) -> bool:
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
        f'Selected files will be deleted. Please confirm',
        btn=QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel,
        icon=QMessageBox.Icon.Question
    )

    if res == QMessageBox.StandardButton.Ok:
        edit_state = ag.file_data_holder.get_edit_state()
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
    ag.file_data_holder.set_data(int(file_id), [])

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
    path = tug.get_app_setting('DEFAULT_EXPORT_PATH', pp.as_posix())
    file_name, ok = QFileDialog.getSaveFileName(parent=ag.app,
        caption='Open file to save list of exported files',
        directory=(Path(path) / 'untitled').as_posix(),
        filter='File list (*.file_list *.json *.txt)'
    )

    if ok:
        fl = QFile(file_name)
        fl.open(QIODeviceBase.OpenModeFlag.WriteOnly)
        _export_files(QTextStream(fl))

def _export_files(out: QTextStream):
    for idx in ag.file_list.selectionModel().selectedRows(0):
        try:
            id = idx.data(Qt.ItemDataRole.UserRole).id
            file_data = db_ut.get_export_data(idx.data(Qt.ItemDataRole.UserRole).id)
        except TypeError:
            continue
        out << f"{json.dumps(file_data)}\n"

def import_files():
    pp = Path('~/fileo/export').expanduser()
    path = tug.get_app_setting('DEFAULT_EXPORT_PATH', pp.as_posix())
    file_name, ok = QFileDialog.getOpenFileName(ag.app,
        caption="Open file to import list of files",
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
            directory=d_path.as_posix()
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

    index = model.index(row, 0, parent)
    model.setData(index, "New folder", Qt.ItemDataRole.EditRole)

    return index

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
    # logger.info(f'{file_id=}, {branch=}')
    ag.file_data_holder.set_data(file_id, branch)
