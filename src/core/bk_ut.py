from loguru import logger

from PyQt6.QtCore import (pyqtSlot, QPoint, QThread,
    QTimer, Qt,
)
from PyQt6.QtGui import QResizeEvent, QKeySequence, QShortcut, QAction
from PyQt6.QtWidgets import QMenu, QTreeView, QHeaderView

from . import (app_globals as ag, low_bk, load_files,
    drag_drop as dd, check_update as upd,
)
from ..widgets import search_files as sf, workers, dup
from ..widgets.cust_msgbox import show_message_box
from .. import tug
from ..widgets.header_field_editor import fieldEditor


def save_bk_settings():
    if not ag.db.conn:
        return
    mode = (
        ag.mode.value
        if ag.mode.value < ag.appMode.RECENT_FILES.value
        else ag.curr_btn_id
    )
    try:
        settings = {
            "TAG_SEL_LIST": low_bk.tag_selection(),
            "EXT_SEL_LIST": low_bk.ext_selection(),
            "AUTHOR_SEL_LIST": low_bk.author_selection(),
            "SHOW_HIDDEN": int(ag.app.show_hidden.isChecked()),
            "DIR_HISTORY": ag.history.get_history(),
            "SELECTED_DIRS" : selected_dirs(),
            "RECENT_FILES": ag.recent_files,
            "APP_MODE": mode,
            "NOTE_EDIT_STATE": ag.file_data.get_edit_state(),
        }
        if ag.mode is ag.appMode.FILTER:
            settings["FILTER_FILE_ID"] = ag.file_list.currentIndex().data(Qt.ItemDataRole.UserRole)
        ag.save_db_settings(**settings)
        if ag.mode is ag.appMode.DIR:
            low_bk.save_curr_file_id(ag.dir_list.currentIndex())
        ag.filter_dlg.save_filter_settings()
    except Exception:
        pass

def selected_dirs() -> list:
    idxs = ag.dir_list.selectionModel().selectedRows()
    branches = []
    for idx in idxs:
        branches.append(ag.define_branch(idx))
    return branches[::-1]

@pyqtSlot()
def search_files():
    if "srchFiles" in ag.popups:
        return
    ff = sf.srchFiles(ag.app.ui.main_pane)
    ff.move(ag.app.ui.main_pane.width() - ff.width() - 222, 22)
    ff.show()
    ff.srch_pattern.setFocus()

def set_menu_more():
    ag.app.ui.more.setIcon(tug.get_icon("more"))
    ag.buttons[ag.app.ui.more.objectName()] = (ag.app.ui.more, "more")
    menu = QMenu(ag.app)
    ttls = tug.get_app_setting('FOLD_TITLES', tug.qss_params['$FoldTitles'])
    for i,item in enumerate(ttls):
        act = QAction(item.title(), ag.app, checkable=True)
        act.setChecked(True)
        act.triggered.connect(lambda state, it = i: ag.signals.hideSignal.emit(state, it))
        menu.addAction(act)

    ag.app.ui.more.setMenu(menu)

def single_shot():
    QTimer.singleShot(5 * 1000, checks)
    QTimer.singleShot(5 * 60 * 1000, run_update0_files)
    QTimer.singleShot(15 * 60 * 1000, run_update_touched_files)

def bk_setup():
    low_bk.dir_view_setup()

    ag.dir_list.customContextMenuRequested.connect(dir_menu)
    ag.file_list.customContextMenuRequested.connect(file_menu)

    if ag.db.conn:
        single_shot()

    dd.set_drag_drop_handlers()

    ag.signals.start_disk_scanning.connect(file_loading)

    ag.tag_list.edit_item.connect(low_bk.tag_changed)
    ag.author_list.edit_item.connect(low_bk.author_changed)
    ag.tag_list.delete_items.connect(low_bk.delete_tags)
    ag.author_list.delete_items.connect(low_bk.delete_authors)

    ag.file_list.doubleClicked.connect(
        lambda: ag.signals.user_signal.emit("double click file"))

    ctrl_w = QShortcut(QKeySequence("Ctrl+W"), ag.dir_list)
    ctrl_w.activated.connect(lambda: ag.signals.user_signal.emit("Dirs Create folder"))
    ctrl_e = QShortcut(QKeySequence("Ctrl+E"), ag.dir_list)
    ctrl_e.activated.connect(lambda: ag.signals.user_signal.emit("Dirs Create folder as child"))
    del_key = QShortcut(QKeySequence(Qt.Key.Key_Delete), ag.dir_list)
    del_key.activated.connect(lambda: ag.signals.user_signal.emit("Dirs Delete folder(s)"))
    act_pref = QShortcut(QKeySequence("Ctrl+,"), ag.app)
    act_pref.activated.connect(lambda: ag.signals.user_signal.emit("MainMenu Preferences"))
    act_theme = QShortcut(QKeySequence("Ctrl+T"), ag.app)
    act_theme.activated.connect(lambda: ag.signals.user_signal.emit("MainMenu Color Themes"))
    esc = QShortcut(QKeySequence(Qt.Key.Key_Escape), ag.app)
    esc.activated.connect(close_last_popup)

def close_last_popup():
    if len(ag.popups) > 0:
        last_key =  next(reversed(ag.popups))
        ag.popups[last_key].close()

@pyqtSlot()
def show_main_menu():
    is_db_opened = bool(ag.db.conn)
    menu = QMenu(ag.app)
    act_new = QAction('New window')
    menu.addAction(act_new)
    menu.addSeparator()
    menu.addAction('Create/Open DB')
    menu.addAction('DB selector')
    menu.addSeparator()
    act_scan = QAction('Scan disk for files')
    act_scan.setEnabled(is_db_opened)
    menu.addAction(act_scan)
    menu.addSeparator()
    act_dup = QAction('Report duplicate files')
    act_dup.setEnabled(is_db_opened)
    menu.addAction(act_dup)
    act_same = QAction('Report files with same names')
    act_same.setEnabled(is_db_opened)
    menu.addAction(act_same)
    menu.addSeparator()
    act_pref = QAction('Preferences', ag.app)
    act_pref.setShortcut(QKeySequence("Ctrl+,"))
    menu.addAction(act_pref)
    act_theme = QAction('Color Themes', ag.app)
    act_theme.setShortcut(QKeySequence("Ctrl+T"))
    menu.addAction(act_theme)
    act_font = QAction('Change font', ag.app)
    menu.addAction(act_font)
    menu.addSeparator()
    menu.addAction('Check for updates')
    menu.addSeparator()
    menu.addAction('About')
    action = menu.exec(ag.app.mapToGlobal(QPoint(54, 26)))
    if action:
        if action.text() == 'Report duplicate files':
            check_duplicates(auto=False)
            return
        ag.signals.user_signal.emit(f"MainMenu {action.text()}")

def resize_section_0():
    hdr = ag.file_list.header()
    ww = ag.file_list.width()
    sz = ww-6 if ag.file_list.verticalScrollBar().isVisible() else ww
    sz0 = sum((hdr.sectionSize(i) for i in range(1, hdr.count())))
    hdr.resizeSection(0, max(sz - sz0, 220))

def set_files_resize_event():
    def file_list_resize(e: QResizeEvent):
        resize_section_0()
        super(QTreeView, ag.file_list).resizeEvent(e)

    ag.file_list.resizeEvent = file_list_resize

def set_field_menu():
    hdr = ag.file_list.header()

    menu = QMenu(ag.app)
    field_list = ag.get_db_setting('FileListFields', tug.qss_params['$FileListFields'])
    field_tips = ag.get_db_setting('ToolTips', tug.qss_params['$ToolTips'])
    for i,field,tt in zip(range(len(field_list)), field_list, field_tips):
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
    resize_section_0()

def restore_dirs():
    restore_history()
    low_bk.set_dir_model()
    low_bk.restore_selected_dirs()
    ag.filter_dlg.restore_filter_settings()
    if ag.mode is ag.appMode.FILTER:
        low_bk.filtered_files()
    elif  ag.mode is ag.appMode.FILTER_SETUP:
        low_bk.show_files([])
    header_restore()

def header_restore():
    hdr: QHeaderView = ag.file_list.header()
    try:
        state = tug.get_app_setting("FILE_LIST_HEADER")
        if state:
            hdr.restoreState(state)
    except Exception as e:
        logger.info(f'{type(e)}; {e.args}', exc_info=True)

    hdr.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
    hdr.sectionResized.connect(resized_column)

    ag.app.ui.field_menu.setIcon(tug.get_icon("more"))
    ag.buttons[ag.app.ui.field_menu.objectName()] = (ag.app.ui.field_menu, "more")
    set_field_menu()
    hdr.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
    hdr.customContextMenuRequested.connect(header_menu)

@pyqtSlot(QPoint)
def header_menu(pos: QPoint):
    hdr: QHeaderView = ag.file_list.header()
    idx = hdr.logicalIndexAt(pos)
    if idx:
        me = QMenu()
        field = ag.get_db_setting('FileListFields', tug.qss_params['$FileListFields'])[idx]
        me.addAction(f'Hide column "{field}"')
        if (idx in (3, 6, 8)) and ('fieldEditor' not in ag.popups):
            me.addAction('Edit title')
        pos = QPoint(pos.x(), hdr.height()+3)
        action = me.exec(hdr.mapToGlobal(pos))
        if action:
            if action.text().startswith('Hide'):
                toggle_show_column(False, idx)
                menu = ag.app.ui.field_menu.menu()
                menu.actions()[idx].setChecked(False)
            elif action.text().startswith('Edit'):
                edit_header_field(idx, pos)

def edit_header_field(idx: int, pos: QPoint):
    editor = fieldEditor(idx, ag.file_list)
    editor.move(pos.x()-editor.width(), pos.y())
    editor.show()

@pyqtSlot(int, int, int)
def resized_column(localIdx: int, oldSize: int, newSize: int):
    if localIdx == 0:
        return
    resize_section_0()

def populate_all():
    if not ag.db.conn:
        return

    low_bk.populate_tag_list()
    low_bk.populate_ext_list()
    low_bk.populate_author_list()

    hide_state = ag.get_db_setting("SHOW_HIDDEN", 0)
    ag.app.show_hidden.setChecked(hide_state)
    ag.app.show_hidden.setIcon(tug.get_icon("show_hide", hide_state))

    ag.file_data.set_edit_state(ag.get_db_setting("NOTE_EDIT_STATE", (False,)))

def restore_history():
    ag.recent_files = ag.get_db_setting('RECENT_FILES', [])
    hist = ag.get_db_setting('DIR_HISTORY', [[], [], -1])
    if len(hist) == 2:
        hist = [[], [], -1]
    logger.info(f'history length: {len(hist[0])}')
    ag.history.set_history(hist)
    low_bk.set_enable_prev_next()
    logger.info(f'next.isEnabled: {ag.app.btn_next.isEnabled()}, prev.isEnabled: {ag.app.btn_prev.isEnabled()}')

@pyqtSlot(QPoint)
def dir_menu(pos):
    idx = ag.dir_list.indexAt(pos)
    menu = QMenu(ag.app)
    if idx.isValid():
        menu.addAction("Create folder\tCtrl-W")
        menu.addAction("Create folder as child\tCtrl-E")
        menu.addSeparator()
        menu.addAction("Toggle hidden state")
        menu.addSeparator()
        menu.addAction("Edit tooltip")
        menu.addSeparator()
        menu.addAction("Copy tree of children")
        menu.addSeparator()
        menu.addAction("Import files")
        menu.addSeparator()
        menu.addAction("Delete folder(s)\tDel")
    else:
        menu.addAction("Create folder\tCtrl-W")

    action = menu.exec(ag.dir_list.mapToGlobal(pos))
    if action:
        item = action.text().split('\t')[0]
        ag.signals.user_signal.emit(f"Dirs {item}")

@pyqtSlot(QPoint)
def file_menu(pos):
    menu = QMenu(ag.app)
    sel_model = ag.file_list.selectionModel()
    if sel_model.currentIndex().isValid():
        menu.addAction("Reveal in explorer")
        menu.addSeparator()
        menu.addAction("Open file")
        menu.addSeparator()
        menu.addAction("Rename file")
        menu.addSeparator()
    if sel_model.hasSelection():
        menu.addAction("Copy file name(s)")
        menu.addAction("Copy full file name(s)")
        menu.addSeparator()
        menu.addAction("Export selected files")
        menu.addSeparator()
    if ag.dir_list.currentIndex().isValid():
        menu.addAction("Create new file")
        menu.addSeparator()
    if ag.mode is ag.appMode.RECENT_FILES:
        menu.addAction("Clear file history")
        if sel_model.hasSelection():
            menu.addAction("Remove selected from history")
    if sel_model.hasSelection():
        menu.addSeparator()
        menu.addAction("Remove file(s) from folder")
        menu.addSeparator()
        menu.addAction("Delete file(s) from DB")
    if len(menu.actions()) > 0:
        action = menu.exec(ag.file_list.mapToGlobal(pos))
        if action:
            ag.signals.user_signal.emit(f"Files {action.text()}")

@pyqtSlot(str, list)
def file_loading(root_path: str, ext: list[str]):
    """
    search for files with a given extension
    in the selected folder and its subfolders
    """
    if not ag.db.conn:
        return

    ag.app.loader = load_files.loadFiles()
    ag.app.loader.set_files_iterator(load_files.yield_files(root_path, ext))
    if ag.app.is_busy:
        ag.start_thread = 'load_files'
    else:
        start_load_files()

def start_load_files():
    ag.app.thread = QThread(ag.app)

    ag.app.loader.moveToThread(ag.app.thread)

    ag.app.thread.started.connect(ag.app.loader.load_data)
    ag.app.loader.finished.connect(finish_loading)
    ag.app.loader.finished.connect(ag.app.loader.deleteLater)

    ag.app.thread.start()
    ag.app.set_busy(True)

@pyqtSlot(bool)
def finish_loading(has_new_ext: bool):
    ag.app.thread.quit()
    ag.app.set_busy(False)
    if has_new_ext:
        ag.signals.user_signal.emit("ext inserted")
    low_bk.dirs_changed(ag.dir_list.currentIndex())

@pyqtSlot()
def checks():
    if int(tug.get_app_setting("CHECK_UPDATE", 0)):
        upd.check4update(True)
        QTimer.singleShot(10 * 1000, check_duplicates)
        return
    check_duplicates()

@pyqtSlot()
def check_duplicates(auto: bool=True):
    if "dlgDup" in ag.popups:
        return
    if auto and not int(tug.get_app_setting("CHECK_DUPLICATES", 1)):
        return
    rep = workers.report_duplicates()
    if rep:
        dup_dialog = dup.dlgDup(rep, ag.app)
        dup_dialog.move(
            (ag.app.width()-dup_dialog.width()) // 3,
            (ag.app.height()-dup_dialog.height()) // 3
        )
        dup_dialog.asked_by_user(not auto)
        dup_dialog.show()
    elif not auto:
        show_message_box(
            "No duplicates found",
            "No file duplicates found in DB"
        )

@pyqtSlot()
def run_update0_files():
    """
    collect data about recently loaded files
    """
    run_worker(workers.update0_files)

@pyqtSlot()
def run_update_touched_files():
    """
    update the data of files opened since the last update
    """
    run_worker(workers.update_touched_files)

def run_worker(func):
    if ag.app.is_busy or not ag.db.conn:
        return
    ag.app.thread = QThread(ag.app)

    ag.app.worker = workers.worker(func)
    ag.app.worker.moveToThread(ag.app.thread)

    ag.app.thread.started.connect(ag.app.worker.run)
    ag.app.worker.finished.connect(finish_worker)
    ag.app.worker.finished.connect(ag.app.worker.deleteLater)

    ag.app.thread.start()
    ag.app.set_busy(True)

@pyqtSlot()
def finish_worker():
    ag.app.thread.quit()
    ag.app.set_busy(False)
    if ag.start_thread == 'load_files':
        ag.start_thread = None
        start_load_files()
