# from loguru import logger
import json
from pathlib import Path
from datetime import datetime
import pickle

from PyQt6.QtCore import (Qt, QSize, QModelIndex,
    pyqtSlot, QUrl, QFile, QTextStream,
    QIODeviceBase, QItemSelectionModel, QPoint,
    QItemSelection,
)
from PyQt6.QtGui import QDesktopServices, QFocusEvent, QAction
from PyQt6.QtWidgets import (QApplication, QAbstractItemView,
    QFileDialog, QMessageBox, QMenu, QToolButton, QStyle, QDialog,
)

from . import (db_ut, app_globals as ag, reports as rep,
    check_update as upd,
)
from .file_model import fileModel, fileProxyModel
from .dir_model import dirModel, dirItem
from ..widgets import about, preferences
from ..widgets.open_db import OpenDB
from ..widgets.font_choosing import fontChooser
from ..widgets.theme_choosing import themeChooser
from ..widgets.scan_disk_for_files import diskScanner
from ..widgets.cust_msgbox import show_message_box
from .. import tug
from .edit_delegates import folderEditDelegate

MAX_WIDTH_DB_DIALOG = 340


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
        "Dirs Copy tree of children": copy_trees,
        "tag_inserted": populate_tag_list,
        "ext inserted": populate_ext_list,
        "author_inserted": populate_author_list,
        "Files Copy file name(s)": copy_file_name,
        "Files Copy full file name(s)": copy_full_file_name,
        "Files Open file": open_current_file,
        "Open file by path": open_with_url,
        "double click file": double_click_file,
        "Files Remove file(s) from folder": remove_files,
        "Files Delete file(s) from DB": ask_delete_files,
        "Files Reveal in explorer": open_file_folder,
        "Files Rename file": rename_file,
        "Files Export selected files": export_files,
        "Files Create new file": create_file,
        "New file created": new_file_created,
        "filter_changed": filtered_files,
        "MainMenu New window": new_instance,
        "MainMenu Create/Open DB": create_open_db,
        "MainMenu DB selector": show_db_list,
        "MainMenu Scan disk for files": scan_disk,
        "MainMenu About": show_about,
        "MainMenu Report files with same names": report_same_names,
        "MainMenu Preferences": set_preferences,
        "MainMenu Color Themes": set_color_themes,
        "MainMenu Change font": change_font,
        "MainMenu Check for updates": upd.check4update,
        "find_files_by_name": find_files_by_name,
        "srch_files_by_note": srch_files_by_note,
        "history_changed": set_enable_prev_next,
        "curr_history_folder": to_history_folder,
        "Enable_buttons": enable_buttons,
        "file-note: Go to file": to_file_by_link,
        "remove_file_from_location": remove_file_from_location,
        "SaveEditState": lambda: ag.save_db_settings(NOTE_EDIT_STATE=ag.file_data.get_edit_state()),
        "show file": single_file,
        "file reveal": reveal_in_explorer,
        "Files Clear file history": clear_recent_files,
        "Files Remove selected from history": remove_files_from_recent,
        "header_field_changed": header_changed,
    }

    @pyqtSlot(str)
    def execute_action(action: str):
        pos = action.find("\\")
        act = action if pos == -1 else action[:pos]
        to_run = data_methods.get(act, None)
        if to_run:
            if pos == -1:
                to_run()
            else:
                to_run(action[pos+1:].strip())
        else:
            show_message_box(
                'Action not implemented',
                f'Action name "{act}" not implemented',
                icon=QStyle.StandardPixmap.SP_MessageBoxWarning
            )

    return execute_action

def set_color_themes():
    if "themeChooser" in ag.popups:
        return
    themes = themeChooser(ag.app)
    pos: QPoint = ag.app.ui.toolBar.mapToGlobal(ag.app.ui.btnSetup.pos())
    themes.move(ag.app.mapFromGlobal(QPoint(pos.x()+85, pos.y()+45)))
    themes.show()
    themes.theme_list.setFocus()

def change_font():
    if "fontChooser" in ag.popups:
        return
    fonts = fontChooser(ag.app)
    pos: QPoint = ag.app.ui.toolBar.mapToGlobal(ag.app.ui.btnSetup.pos())
    fonts.move(ag.app.mapFromGlobal(QPoint(pos.x()+65, pos.y()+65)))
    fonts.show()

def header_changed(val: str):
    ag.file_data.reset_file_info(val)
    model: fileProxyModel = ag.file_list.model()
    model.update_header(val)
    if val[0] in "38":
        ag.filter_dlg.set_ed_fields(val[0])

def create_file():
    model:  fileProxyModel = ag.file_list.model()
    smodel: fileModel = model.sourceModel()
    idx = ag.file_list.currentIndex()
    sidx = model.mapToSource(idx)
    row = sidx.row()+1
    if smodel.insertRow(row):
        sidx = smodel.index(row, 0)
        idx = model.mapFromSource(sidx)
        ag.file_list.edit(idx)

def copy_trees():
    ss = '¹²'
    legend = f'\nLegend: {ss[0]} - single folder, {ss[1]} - multy'
    def children(ini: list):
        dd = []
        for name1, id1 in ini:
            first = f'{name1}/' if id1 else ''
            for name2, id2, mu in db_ut.children_names(id1):
                vv = (f'{first}{name2}{ss[mu]}', id2)
                if db_ut.has_children(id2):
                    dd.append(vv)
                else:
                    tt.append(vv)
        if dd:
            children(dd)

    idxs = ag.dir_list.selectionModel().selectedIndexes()
    dirs = []
    tt = []
    model: dirModel = ag.dir_list.model()
    for idx in idxs:
        udat: ag.DirData = idx.data(Qt.ItemDataRole.UserRole)
        vv = (f'{idx.data(Qt.ItemDataRole.DisplayRole)}{ss[udat.multy]}', udat.dir_id)
        if model.getItem(idx).childCount():
            dirs.append(vv)
        else:
            tt.append(vv)

    children(dirs)
    qq = [x[0] for x in tt]
    qq.sort(key=str.lower)
    qq.append(legend)
    QApplication.clipboard().setText('\n'.join(qq))

@pyqtSlot()
def refresh_dir_list():
    branch = ag.define_branch(ag.dir_list.currentIndex())
    set_dir_model()
    idx = expand_branch(branch)
    if not idx.isValid():
        idx = ag.dir_list.model().index(0, 0, QModelIndex())

    ag.dir_list.setCurrentIndex(idx)

def new_instance(db_name: str=''):
    tug.save_app_setting(MainWindowGeometry=ag.app.normalGeometry())
    tug.new_window(db_name)

def clear_recent_files():
    ag.recent_files.clear()
    ag.switch_to_prev_mode()
    refresh_file_list()

def remove_files_from_recent():
    for idx in ag.file_list.selectionModel().selectedRows(0):
        ag.recent_files.remove(idx.data(Qt.ItemDataRole.UserRole))
    show_recent_files()

def save_db_list_at_close():
    db_open = ag.popups["OpenDB"] if "OpenDB" in ag.popups else OpenDB(ag.app)
    db_open.save_db_list(ag.db.path)

def show_db_list():
    """
    manage the list of db files,
    select DB to open
    """
    if "OpenDB" in ag.popups:
        ag.popups["OpenDB"].close()
        return

    open_db = OpenDB(ag.app)
    open_db.move(48, 20)
    open_db.resize(
        min(ag.app.width() // 2, MAX_WIDTH_DB_DIALOG),
        ag.app.height() - 60)
    open_db.show()
    open_db.listDB.setFocus()

def create_open_db():
    db_open = ag.popups["OpenDB"] if "OpenDB" in ag.popups else OpenDB(ag.app)
    db_open.add_db()

def init_db(db_path: str):
    if db_path:
        db_open = OpenDB(ag.app)
        if db_open.open_existed(db_path):
            return
        db_open.close()
    ag.app.ui.db_name.setText('Click to select DB')

def scan_disk():
    """
    search for files with a given extension
    in the selected folder and its subfolders
    """
    if not ag.db.conn or "diskScanner" in ag.popups:
        return
    take_files = diskScanner(ag.app)
    take_files.move(
        (ag.app.width()-take_files.width()) // 4,
        (ag.app.height()-take_files.height()) // 4)
    take_files.show()

def get_branch(dir_id: int) -> list:
    branch = [dir_id]
    while dir_id:
        dir_id = db_ut.dir_min_parent(dir_id)
        if dir_id:
            branch.append(dir_id)
    branch.reverse()
    return branch

def to_file_by_link(param: str):
    file_id, *branch = param.split('-')
    if not branch:
        dir_id = db_ut.get_dir_id_for_file(file_id)
        brnch = get_branch(dir_id)
    else:
        brnch = [int(it) for it in branch[0].split(',')]
    brnch.append(False)           # expand branch
    idx = expand_branch(brnch)

    if idx.isValid():
        if ag.mode is not ag.appMode.DIR:
            btn = ag.app.ui.toolbar_btns.button(ag.appMode.DIR.value)
            btn.setChecked(True)
            ag.set_mode(ag.appMode.DIR)
            refresh_file_list()
        ag.dir_list.setCurrentIndex(idx)
        ag.dir_list.scrollTo(idx, QAbstractItemView.ScrollHint.PositionAtCenter)
        set_current_file(int(file_id))

def report_same_names():
    rep_creator = rep.sameFileNames()
    repo = rep_creator.get_report()
    if repo:
        save_same_names_report(repo)
    else:
        show_message_box(
            'Files with same names',
            "No files with same names found",
        )

def save_same_names_report(rep: list):
    pp = Path('~/fileo/report').expanduser()
    path = Path(
        tug.get_app_setting('DEFAULT_REPORT_PATH', str(pp))
    ) / f"same_names.{ag.app.ui.db_name.text()}.log"
    with open(path, "w") as out:
        out.write(f'Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
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
    ag.app.ui.btnFilter.setEnabled(True)
    ag.app.ui.btnFilterSetup.setEnabled(True)

def rename_file():
    idx: QModelIndex = ag.file_list.currentIndex()
    idx = ag.file_list.model().index(idx.row(), 0)
    ag.file_list.edit(idx)

def set_enable_prev_next():
    foll, prev = ag.history.is_next_prev_enable()
    ag.app.btn_next.setEnabled(foll)
    ag.app.btn_prev.setEnabled(prev)
    if foll or prev:
        menu = create_history_menu()
        ag.app.btn_prev.setMenu(menu)
        ag.app.btn_next.setMenu(menu)

def create_history_menu() -> QMenu:
    menu = QMenu(ag.app)
    hist, _, curr = ag.history.get_history()
    dd = len(hist)
    for i,it in enumerate(hist[::-1], 1):
        *_,leaf = it.split(',')
        if dir_name := db_ut.get_dir_name(leaf):
            act:QAction = QAction(dir_name, ag.app, checkable=True)
            act.triggered.connect(lambda state, rr=dd-i: ag.history.set_current(rr))
            if dd-i == curr:
                act.setChecked(True)
            menu.addAction(act)
    return menu

def show_history_menu(pos: QPoint, btn: QToolButton):
    btn.menu().exec(btn.mapToGlobal(QPoint(0, btn.y() + btn.height())))

def srch_files_by_note():
    row_cnt = srch_files_common(ag.appMode.FOUND_IN_NOTES, db_ut.get_all_notes())
    searching = ag.popups['srchInNotes'].search_text()
    if row_cnt:
        ag.app.ui.files_heading.setText(f'Found files, text in notes "{searching}"')
        ag.file_list.setFocus()
    else:
        show_message_box('Search in notes',
            f'Text "{searching}" not found in notes!',
            icon=QStyle.StandardPixmap.SP_MessageBoxWarning)

def srch_files_common(mode: ag.appMode, search_in) -> int:
    search_expression = ag.popups[{'FOUND_FILES': 'srchFiles', 'FOUND_IN_NOTES': 'srchInNotes'}[mode.name]].srch_prepare()

    db_ut.clear_temp()
    last_id = 0
    found_ids = []
    for file_id, in_text in search_in:
        if file_id == last_id:
            continue
        if search_expression(in_text):
            found_ids.append((file_id,))
            last_id = file_id

    db_ut.save_to_temp(mode.name, found_ids)
    if len(found_ids) > 0:
        ag.set_mode(mode)
    if ag.mode is ag.appMode.FOUND_IN_NOTES:
        ag.file_data.set_notes_search_options()
    return show_files(db_ut.get_found_files(), 0, False)

def find_files_by_name():
    row_cnt = srch_files_common(ag.appMode.FOUND_FILES, db_ut.get_file_names())
    searching = ag.popups['srchFiles'].search_text()
    if row_cnt:
        ag.app.ui.files_heading.setText(f'Found files "{searching}"')
        ag.file_list.setFocus()
    else:
        show_message_box('Search files',
            f'File "{searching}" not found!',
            icon=QStyle.StandardPixmap.SP_MessageBoxWarning)

def set_preferences():
    if "Preferences" in ag.popups:
        return
    prefs = preferences.Preferences(ag.app)
    prefs.move(
        (ag.app.width()-prefs.width()) // 3,
        (ag.app.height()-prefs.height()) // 3
    )
    prefs.show()

def show_about():
    if "AboutDialog" in ag.popups:
        return
    about_dialog = about.AboutDialog(ag.app)
    about_dialog.move(
        (ag.app.width()-about_dialog.width()) // 3,
        (ag.app.height()-about_dialog.height()) // 3
    )
    about_dialog.show()

#region Common
def save_branch(index: QModelIndex):
    branch = ag.define_branch(index)
    branch[-1] = 1
    db_ut.save_branch_in_aux(pickle.dumps(branch))

def restore_branch() -> QModelIndex:
    val = db_ut.get_branch_from_aux()
    return expand_branch(pickle.loads(val) if val else [])

def get_dir_names_path(index: QModelIndex) -> list:
    item: dirItem = index.internalPointer()
    branch = []
    while item:
        if not item.parent():
            break
        branch.append(item.data())    # dir name
        item = item.parent()
    branch.reverse()
    return branch

def expand_branch(branch: list) -> QModelIndex:
    model = ag.dir_list.model()
    parent = QModelIndex()
    if not branch:
        return parent
    model = ag.dir_list.model()
    item: dirItem = model.rootItem
    expanded = branch[-1]
    for it in branch[:-1]:
        for i,child in enumerate(item.children):
            ud = child.user_data()
            if it == ud.dir_id:
                parent = model.index(i, 0, parent)
                item = child
                if expanded:
                    ag.dir_list.setExpanded(parent, True)
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

    ag.dir_list.selectionModel().selectionChanged.connect(ag.filter_dlg.dir_selection_changed)
    ag.dir_list.selectionModel().currentRowChanged.connect(cur_dir_changed)

def restore_selected_dirs():
    branches = ag.get_db_setting("SELECTED_DIRS", [])
    if not branches:
        show_files([])
        return
    selection = QItemSelection()
    for br in branches:
        idx = expand_branch(branch=br)
        selection.select(idx, idx)

    to_history_folder()
    model = ag.dir_list.selectionModel()
    model.clearSelection()
    model.select(selection, QItemSelectionModel.SelectionFlag.Select)

@pyqtSlot(QModelIndex, QModelIndex)
def cur_dir_changed(curr_idx: QModelIndex, prev_idx: QModelIndex):
    # logger.info(f'prev: {prev_idx.data(Qt.ItemDataRole.DisplayRole)}, curr: {curr_idx.data(Qt.ItemDataRole.DisplayRole)}')
    if curr_idx.isValid():
        ag.app.ui.folder_path.setText('>'.join(get_dir_names_path(curr_idx)))
        if ag.mode is ag.appMode.DIR:
            ag.history.add_item(ag.define_branch(curr_idx))
            save_curr_file_id(prev_idx)
            show_folder_files()

def dirlist_get_focus(e: QFocusEvent):
    if e.reason() is Qt.FocusReason.ActiveWindowFocusReason:
        return
    if ag.mode.value < ag.appMode.RECENT_FILES.value:
        return
    ag.switch_to_prev_mode()
    refresh_file_list()

def save_curr_file_id(dir_idx: QModelIndex):
    """ save id of current file in dir (folder) """
    if dir_idx.isValid():
        file_idx = ag.file_list.currentIndex()
        if file_idx.isValid():
            file_id = file_idx.data(Qt.ItemDataRole.UserRole)
            u_dat = update_file_id_in_dir_model(file_id, dir_idx)
            db_ut.save_file_id(u_dat)

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
def refresh_file_list():
    if ag.mode is ag.appMode.DIR:
        show_folder_files()
    elif ag.mode is ag.appMode.FILTER:
        filtered_files()

@pyqtSlot()
def to_prev_folder():
    ag.history.prev_dir()
    to_history_folder()

@pyqtSlot()
def to_next_folder():
    ag.history.next_dir()
    to_history_folder()

@pyqtSlot()
def to_history_folder():
    idx = expand_branch(ag.history.get_current())
    if idx.isValid():
        ag.dir_list.setCurrentIndex(idx)
        ag.dir_list.scrollTo(idx, QAbstractItemView.ScrollHint.PositionAtCenter)

def filtered_files():
    ag.app.ui.files_heading.setText('filtered files')
    file_id = ag.get_db_setting("FILTER_FILE_ID", 0)
    show_files(ag.filter_dlg.get_file_list(), file_id)

def show_folder_files():
    idx = ag.dir_list.currentIndex()
    if idx.isValid():
        ag.app.ui.files_heading.setText(
            f'files from folder "{idx.data(Qt.ItemDataRole.DisplayRole)}"'
        )
        u_dat: ag.DirData = idx.data(Qt.ItemDataRole.UserRole)
        show_files(db_ut.get_files(u_dat.dir_id, u_dat.parent), u_dat.file_id)
    else:
        show_files([])

def show_recent_files():
    ag.app.ui.files_heading.setText('Recent files')
    # logger.info('>>> before show_files()')
    show_files(get_recent_files())
    ag.file_list.setFocus()

def get_recent_files() -> list:
    ''' in LIFO order '''
    ag.set_mode(ag.appMode.RECENT_FILES)
    return (db_ut.get_file(idx) for idx in ag.recent_files[::-1])

def show_files(files, cur_file: int = 0, show_empty: bool = True) -> int:
    """
    populate file's model
    :@param files - list of file
    :@param cur_file - set current file, 0 is on first line
    """
    ag.file_list.setSortingEnabled(ag.mode is not ag.appMode.RECENT_FILES)
    model: fileModel = fileModel()
    model.fill_model(files)
    file_cnt = model.rowCount()
    ag.app.ui.file_count.setText(f"files: {file_cnt}")
    if file_cnt == 0:
        file_notes_show(QModelIndex())
    if file_cnt or show_empty:
        set_file_model(model)
        ag.file_list.selectionModel().currentRowChanged.connect(current_file_changed)
        set_current_file(cur_file)
    return file_cnt

def single_file(file_id: str):
    if ag.mode is ag.appMode.DIR:
        save_curr_file_id(ag.dir_list.currentIndex())
    elif ag.mode is ag.appMode.FILTER:
        ag.save_db_settings(FILTER_FILE_ID=ag.file_list.currentIndex().data(Qt.ItemDataRole.UserRole))
    ag.set_mode(ag.appMode.FILE_BY_REF)
    ag.app.ui.files_heading.setText('single_file')
    # logger.info('>>> before show_files()')
    show_files([db_ut.get_file(file_id)])
    ag.file_list.setFocus()

def set_current_file(file_id: int):
    model: fileProxyModel = ag.file_list.model()
    if file_id == 0:
        ag.file_list.setCurrentIndex(model.index(0, 0))
        return

    idx = model.get_index_by_id(file_id)
    if idx.isValid():
        ag.file_list.setCurrentIndex(idx)
        ag.file_list.scrollTo(idx)
    else:
        ag.file_list.setCurrentIndex(model.index(0, 0))

def set_file_model(model: fileModel):
    proxy_model = fileProxyModel()
    proxy_model.setSourceModel(model)
    proxy_model.setSortRole(Qt.ItemDataRole.UserRole+1)
    ag.file_list.setModel(proxy_model)

@pyqtSlot(QModelIndex, QModelIndex)
def current_file_changed(curr: QModelIndex, prev: QModelIndex):
    if curr.isValid():
        ag.file_list.scrollTo(curr)
        ag.app.ui.current_filename.setText(file_name(curr))
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

def open_file_folder():
    idx = ag.file_list.currentIndex()
    if idx.isValid():
        tug.reveal_file(full_file_name(idx))
        ag.add_recent_file(idx.data(Qt.ItemDataRole.UserRole))

def reveal_in_explorer(file_id: int|str):
    tug.reveal_file(db_ut.get_file_path(file_id))

def full_file_name(index: QModelIndex) -> str:
    return db_ut.get_file_path(index.data(Qt.ItemDataRole.UserRole))

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

def new_file_created(file_id: str):
    set_current_file(int(file_id))
    open_current_file()
    file_notes_show(ag.file_list.currentIndex())

def open_file_by_model_index(index: QModelIndex):
    cnt = db_ut.duplicate_count(index.data(Qt.ItemDataRole.UserRole))
    if cnt[0] > 1:
        show_message_box(
            "Duplicated file",
            (f"There are {cnt} files with the same context\n"
             "It is highly recommended to remove duplicate files;\n"
             "the file will not be opened."),
             icon=QStyle.StandardPixmap.SP_MessageBoxWarning
        )
        return
    if open_with_url(full_file_name(index)):
        update_open_date(index)
    else:
        open_manualy(index)
    ag.add_recent_file(index.data(Qt.ItemDataRole.UserRole))

def open_with_url(path: str) -> bool:
    url = QUrl()
    return QDesktopServices.openUrl(url.fromLocalFile(path))

def update_open_date(index: QModelIndex):
    ts = db_ut.update_opened_file(index.data(Qt.ItemDataRole.UserRole))
    if ts > 0:
        ag.file_list.model().update_opened(ts, index)

def ask_delete_files():
    """
    delete file from DB
    """
    def delete_files(result: int):
        if result == QDialog.DialogCode.Accepted.value:
            edit_state = ag.file_data.get_edit_state()
            ed_file_id = edit_state[1] if edit_state[0] else 0
            row = ag.file_list.model().rowCount()
            skip_edited = False
            for idx in ag.file_list.selectionModel().selectedRows(0):
                del_file_id = idx.data(Qt.ItemDataRole.UserRole)
                if del_file_id == ed_file_id:
                    skip_edited = True
                    continue
                row = min(row, idx.row())
                db_ut.delete_file(del_file_id)
            if skip_edited:
                show_message_box(
                    'Not deleted',
                    f'File "{db_ut.get_file_name(ed_file_id)}", '
                    'a note is editing')
            post_delete_file(row)

    if not ag.file_list.selectionModel().hasSelection():
        return

    show_message_box(
        'delete file from DB',
        'Selected files will be deleted. Please confirm',
        btn=QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel,
        icon=QStyle.StandardPixmap.SP_MessageBoxQuestion,
        callback=delete_files
    )

def remove_files():
    '''
    delete file from folder only
    '''
    row = ag.file_list.model().rowCount()
    for idx in ag.file_list.selectionModel().selectedRows(0):
        row = min(row, idx.row())
        file_id = idx.data(Qt.ItemDataRole.UserRole)
        dir_id = get_dir_id(file_id)
        db_ut.delete_file_dir_link(file_id, dir_id)
    post_delete_file(row)

def remove_file_from_location(param: str):
    file_id, dir_id = param.split(',')
    db_ut.delete_file_dir_link(file_id, dir_id)
    ag.file_data.set_data(int(file_id))

def get_dir_id(file: int) -> int:
    """
    in case of appMode.DIR - returns id of current folder
    otherwise - returns id of arbitrary folder contained current file
    """
    if ag.mode is ag.appMode.DIR or ag.filter_dlg.is_single_folder():
        dir_idx = ag.dir_list.currentIndex()
        dir_dat: ag.DirData = dir_idx.data(Qt.ItemDataRole.UserRole)
        return dir_dat.dir_id

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
    def get_notes():
        def file_ids_in_note():
            txt, *_ = note
            pos = txt.find('fileid:/')
            while pos > 0:      # pos can't be 0
                pos2 = txt.find(')', pos)
                file_id = int(txt[pos+8:pos2])
                if file_id not in ids:
                    active_next.add(file_id)
                    ids.add(file_id)
                pos = txt.find('fileid:/', pos2)

        active = set(ids)
        while active:
            active_next = set()
            for it in active:
                file_notes = []
                for note in db_ut.get_file_notes(it):
                    file_ids_in_note()
                    file_notes.append(note)
                notes[it] = file_notes
            active = active_next

    ids = set()
    for idx in ag.file_list.selectionModel().selectedRows(0):
        ids.add(idx.data(Qt.ItemDataRole.UserRole))

    notes = {}
    get_notes()

    app_v = ag.app_version()
    db_v = ag.db.conn.cursor().execute("PRAGMA user_version").fetchone()[0]
    out << json.dumps({'app_v': app_v, 'db_v': db_v}) << "\n"

    for idn in ids:
        try:
            file_data = db_ut.get_file_export(idn)
        except TypeError:
            continue
        file_data['notes'] = notes[idn]
        file_data['id'] = idn
        out << json.dumps(file_data) << "\n"

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
        _import_files(QTextStream(fp), ag.dir_list.currentIndex(), ag.fileSource.IMPORT_DB)

def _import_files(fp: QTextStream, target: QModelIndex, source: ag.fileSource = ag.fileSource.DRAG_DB):
    def load_file(fl: dict) -> int:
        nonlocal file_ids, new_tag, new_auther, new_ext
        a_file = fl['file']
        f_path: Path = Path(a_file[-1]) / a_file[1]
        if not f_path.is_file():
            return 0

        dir_id = target.data(Qt.ItemDataRole.UserRole).dir_id
        file_id = db_ut.registered_file_id(a_file[-1], a_file[1])
        if not file_id:
            file_id, is_new_ext = db_ut.insert_file(a_file, added_ts, source.value)
            new_ext |= is_new_ext
        db_ut.copy_file(file_id, dir_id)

        file_ids[fl['id']] = file_id

        new_tag |= db_ut.insert_tags(file_id, fl['tags'])
        db_ut.insert_filenotes(file_id, fl['notes'])
        new_auther |= db_ut.insert_authors(file_id, fl['authors'])

    def reset_file_ids_in_notes():
        def replace_file_id(note):
            txt, f_id, note_id, *_ = note
            pp = pos = txt.find('fileid:/')
            while pos > 0:      # pos can't be 0
                pos2 = txt.find(')', pos)
                file_id = txt[pos+8:pos2]
                if int(file_id) in file_ids:
                    txt = txt.replace(file_id, str(file_ids[int(file_id)]))
                pos = txt.find('fileid:/', pos2)
            if pp:
                db_ut.update_note_exported(f_id, note_id, txt)

        for new_id in file_ids.values():
            for note in db_ut.get_file_notes(new_id):
                replace_file_id(note)

    file_ids = {}
    new_tag = new_auther = new_ext = False
    added_ts = int(datetime.now().replace(microsecond=0).timestamp())

    vers = json.loads(fp.readLine())
    if vers.get('app_v', '') == ag.app_version():
        db_v = ag.db.conn.cursor().execute("PRAGMA user_version").fetchone()[0]
        if vers.get('db_v', '') == db_v:
            while not fp.atEnd():
                load_file(json.loads(fp.readLine()))

            reset_file_ids_in_notes()

            if new_tag:
                populate_tag_list()
                ag.tag_list.list_changed.emit()
            if new_auther:
                populate_author_list()
                ag.author_list.list_changed.emit()
            if new_ext:
                populate_ext_list()
            if target == ag.dir_list.currentIndex():
                refresh_file_list()
        else:
            show_message_box('Data from Wrong version of DB',
                f'Data DB v. = {vers.get("db_v", '')}, current DB v. = {db_v}'
            )
    else:
        show_message_box('Data from Wrong version of application',
            f'Data app.v. = {vers.get("app_v", '')}, current app.v. = {ag.app_version()}'
        )
#endregion

#region  Files - Dirs
def open_manualy(index: QModelIndex):
    def msg_callback(res: int):
        if res == 1:
            path = full_file_name(index)
            i_path = Path(path)
            d_path = i_path.parent
            while not d_path.exists():
                d_path = d_path.parent
            filename, ok = QFileDialog.getOpenFileName(ag.app, directory=str(d_path))

            if ok:
                f_path = Path(filename)
                path_id = db_ut.get_path_id(f_path.parent.as_posix())
                id = index.data(Qt.ItemDataRole.UserRole)
                db_ut.update_file_name_path(id, path_id, f_path.name)
                open_with_url(str(f_path))

    show_message_box(
        'File cannot be opened',
        'Please, select file',
        btn=QMessageBox.StandardButton.Open | QMessageBox.StandardButton.Cancel,
        icon=QStyle.StandardPixmap.SP_MessageBoxQuestion,
        callback=msg_callback
    )

def create_child_dir():
    if ag.app.focusWidget() is not ag.dir_list:
        return
    cur_idx = ag.dir_list.selectionModel().currentIndex()

    new_idx = insert_dir_row(0, cur_idx)

    if new_idx.isValid():
        create_folder(new_idx)
        ag.dir_list.setExpanded(cur_idx, True)
        ag.dir_list.clearSelection()
        ag.dir_list.setCurrentIndex(new_idx)
        ag.dir_list.edit(new_idx)

def insert_dir_row(row: int, parent: QModelIndex) -> QModelIndex:
    model = ag.dir_list.model()
    if not model.insertRow(row, parent):
        return QModelIndex()
    return model.index(row, 0, parent)

def create_dir():
    if ag.app.focusWidget() is not ag.dir_list:
        return
    cur_idx = ag.dir_list.currentIndex()

    new_idx = insert_dir_row(cur_idx.row()+1, cur_idx.parent())

    if new_idx.isValid():
        create_folder(new_idx)
        ag.dir_list.clearSelection()
        ag.dir_list.setCurrentIndex(new_idx)
        ag.dir_list.edit(new_idx)

def create_folder(index: QModelIndex):
    parent = index.parent()
    parent_id = parent.data(Qt.ItemDataRole.UserRole).dir_id if parent.isValid() else 0
    dir_id = db_ut.insert_dir("New folder", parent_id)

    user_data = ag.DirData(parent=parent_id, dir_id=dir_id)
    item: dirItem = index.internalPointer()
    item.setUserData(user_data)
    item.setData("New folder", Qt.ItemDataRole.EditRole)

def delete_folders():
    def index_to() -> QModelIndex:
        cur_idx = ag.dir_list.currentIndex()
        cnt = ag.dir_list.model().rowCount(cur_idx.parent())
        if cnt > 1:
            row = cur_idx.row()
            return cur_idx.siblingAtRow(row-1 if row > 0 else row+1)
        return cur_idx.parent()

    if ag.app.focusWidget() is not ag.dir_list:
        return
    to_idx = index_to()

    for idx in ag.dir_list.selectionModel().selectedRows(0):
        u_dat: ag.DirData = idx.data(Qt.ItemDataRole.UserRole)
        if not db_ut.break_link(u_dat.dir_id, u_dat.parent):
            delete_tree(u_dat.dir_id)
    dirs_changed(to_idx)
    ag.history.check_remove()
    set_enable_prev_next()

def delete_tree(parent: int):
    for dir_id in db_ut.dir_children(parent):
        if not db_ut.break_link(dir_id, parent):
            delete_tree(dir_id)

def dirs_changed(index: QModelIndex, sure_expand: bool=False):
    branch = ag.define_branch(index)
    set_dir_model()
    if index.isValid():
        if sure_expand:
            branch[-1] = 1
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
        if u_dat.dir_id:
            u_dat.hidden = not u_dat.hidden
            db_ut.update_hidden_state(u_dat.dir_id, u_dat.parent, u_dat.hidden)
            model.getItem(idx).setUserData(u_dat)
#endregion

#region  Tags
def populate_tag_list():
    ag.tag_list.set_list(db_ut.get_tags())
    sel = ag.get_db_setting("TAG_SEL_LIST", [])
    ag.tag_list.set_selection(sel)

def tag_selection() -> list:
    return ag.tag_list.get_selected_ids()

def tag_changed(new_tag: str):
    if new_tag == ag.tag_list.get_current():   # edit finished, but tags not changed
        return
    cur_id = ag.tag_list.current_id()
    db_ut.update_tag(cur_id, new_tag)
    populate_tag_list()
    ag.tag_list.set_selection((cur_id,))
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
    sel = ag.get_db_setting("EXT_SEL_LIST", [])
    ag.ext_list.set_selection(sel)

def ext_selection() -> list:
    return ag.ext_list.get_selected_ids()

#region  Authors
def populate_author_list():
    ag.author_list.set_list(db_ut.get_authors())
    sel = ag.get_db_setting("AUTHOR_SEL_LIST", [])
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
        file_idx.data(Qt.ItemDataRole.UserRole)
        if file_idx.isValid() else 0
    )
    ag.file_data.set_data(file_id)
