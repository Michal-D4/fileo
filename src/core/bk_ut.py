from loguru import logger
from typing import TYPE_CHECKING

from PyQt6.QtCore import (QModelIndex, pyqtSlot, QPoint, QThread,
    QTimer, Qt,
)
from PyQt6.QtGui import QResizeEvent, QKeySequence, QShortcut, QAction
from PyQt6.QtWidgets import (QMenu, QTreeView, QHeaderView,
    QMessageBox,
)

from . import (app_globals as ag, low_bk, load_files,
    drag_drop as dd,
)
from ..widgets import workers, find_files, dup
from .. import tug

if TYPE_CHECKING:
    from .sho import shoWindow

self: 'shoWindow' = None
min_width = 220

tool_tips = (
    ",Last opening date,rating of file,number of file openings,"
    "Last modified date,Number of pages(in book),Size of file,"
    "Publication date(book),Date of last note,File creation date"
).split(',')

def save_bk_settings():
    if not ag.db.conn:
        return
    mode = (
        ag.mode.value
        if ag.mode.value <= ag.appMode.HISTORY_FILES.value
        else ag.first_mode.value
    )
    try:
        settings = {
            "FILE_LIST_HEADER": ag.file_list.header().saveState(),
            "TAG_SEL_LIST": low_bk.tag_selection(),
            "EXT_SEL_LIST": low_bk.ext_selection(),
            "AUTHOR_SEL_LIST": low_bk.author_selection(),
            "SHOW_HIDDEN": int(self.show_hidden.isChecked()),
            "DIR_HISTORY": ag.history.get_history(),
            "FILE_HISTORY": ag.file_history,
            "APP_MODE": mode,
            "NOTE_EDIT_STATE": ag.file_data.get_edit_state(),
            "FILTER_FILE_ROW": (
                ag.file_list.currentIndex().row()
                if ag.mode is ag.appMode.FILTER else 0
            ),
            "SELECTED_DIRS" : selected_dirs(),
        }
        ag.save_settings(**settings)
        dir_idx = ag.dir_list.currentIndex()

        low_bk.save_file_id(dir_idx)
        ag.filter_dlg.save_filter_settings()
    except:
        pass

def selected_dirs() -> list:
    idxs = ag.dir_list.selectionModel().selectedIndexes()
    branches = []
    for idx in idxs:
        branches.append(low_bk.define_branch(idx))
    return branches

@pyqtSlot()
def search_files():
    ff = find_files.findFile(ag.app)
    ff.move(ag.app.width() - ff.width() - 40, 40)
    ff.show()
    ff.srch_pattern.setFocus()

@pyqtSlot(bool)
def toggle_collapse(collapse: bool):
    if collapse:
        low_bk.save_branch_in_temp(ag.dir_list.currentIndex())
        ag.dir_list.collapseAll()
    else:
        idx = low_bk.restore_branch_from_temp()
        ag.dir_list.setCurrentIndex(idx)

def set_menu_more(self):
    self.ui.more.setIcon(tug.get_icon("more"))
    ag.buttons.append((self.ui.more, "more"))
    menu = QMenu(self)
    for i,item in enumerate(tug.qss_params['$FoldTitles'].split(',')):
        act = QAction(item, self, checkable=True)
        act.setChecked(True)
        act.triggered.connect(
            # lambda state, it = i: self.set_hidden(state, seq=it)
            lambda state, it = i: ag.signals_.hideSignal.emit(state, it)
        )
        menu.addAction(act)

    self.ui.more.setMenu(menu)

def bk_setup(main: 'shoWindow'):
    ag.file_list.resizeEvent = file_list_resize_0
    low_bk.dir_dree_view_setup()
    ag.file_list.currentChanged = current_file_changed

    ag.dir_list.customContextMenuRequested.connect(dir_menu)
    ag.file_list.customContextMenuRequested.connect(file_menu)

    if ag.db.conn:
        populate_all()

        QTimer.singleShot(10 * 1000, show_lost_files)
        if bool(tug.get_app_setting("CHECK_DUPLICATES", 0)):
            QTimer.singleShot(5 * 1000, check_duplicates)
        QTimer.singleShot(5 * 60 * 1000, run_update0_files)
        QTimer.singleShot(15 * 60 * 1000, run_update_touched_files)
        QTimer.singleShot(25 * 60 * 1000, run_update_pdf_files)

    dd.set_drag_drop_handlers()

    ag.signals_.start_disk_scanning.connect(file_loading)
    ag.signals_.app_mode_changed.connect(low_bk.app_mode_changed)

    ag.tag_list.edit_item.connect(low_bk.tag_changed)
    ag.author_list.edit_item.connect(low_bk.author_changed)
    ag.tag_list.delete_items.connect(low_bk.delete_tags)
    ag.author_list.delete_items.connect(low_bk.delete_authors)

    ag.file_list.doubleClicked.connect(
        lambda: ag.signals_.user_signal.emit("double click file"))

    ctrl_f = QShortcut(QKeySequence("Ctrl+f"), ag.app)
    ctrl_f.activated.connect(search_files)
    ctrl_w = QShortcut(QKeySequence("Ctrl+w"), ag.app)
    ctrl_w.activated.connect(short_create_folder)
    ctrl_e = QShortcut(QKeySequence("Ctrl+e"), ag.app)
    ctrl_e.activated.connect(short_create_child)
    del_key = QShortcut(QKeySequence(Qt.Key.Key_Delete), ag.app)
    del_key.activated.connect(short_delete_folder)

@pyqtSlot()
def short_create_folder():
    if ag.app.focusWidget() is not ag.dir_list:
        return
    ag.signals_.user_signal.emit(f"Dirs Create folder")

@pyqtSlot()
def short_create_child():
    if ag.app.focusWidget() is not ag.dir_list:
        return
    if ag.dir_list.currentIndex().isValid():
        ag.signals_.user_signal.emit(f"Dirs Create folder as child")

@pyqtSlot()
def short_delete_folder():
    if ag.app.focusWidget() is not ag.dir_list:
        return
    if ag.dir_list.currentIndex().isValid():
        if ag.show_message_box(
            'Delete folders',
            'Delete selected folders. Please confirm',
            btn=QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel,
            icon=QMessageBox.Icon.Question
        ) == QMessageBox.StandardButton.Ok:
            ag.signals_.user_signal.emit(f"Dirs Delete folder(s)")

@pyqtSlot()
def show_main_menu():
    is_db_opened = bool(ag.db.conn)
    menu = QMenu(self)
    act_new = QAction('New window')
    act_new.setEnabled(not ag.single_instance)
    menu.addAction(act_new)
    menu.addSeparator()
    menu.addAction('Create/Open DB')
    menu.addAction('Select DB from list')
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
    menu.addAction('Preferences')
    menu.addSeparator()
    menu.addAction('Check for update')
    menu.addSeparator()
    menu.addAction('About')
    pos = self.ui.btnSetup.pos()
    action = menu.exec(ag.app.mapToGlobal(
        pos + QPoint(53, 26)
    ))
    if action:
        if action.text() == 'Report duplicate files':
            check_duplicates(auto=False)
            return
        ag.signals_.user_signal.emit(f"MainMenu {action.text()}")

@pyqtSlot(QModelIndex, QModelIndex)
def current_file_changed(curr: QModelIndex, prev: QModelIndex):
    if curr.isValid():
        ag.file_list.scrollTo(curr)
        self.ui.current_filename.setText(low_bk.file_name(curr))
        low_bk.file_notes_show(curr)

def resize_section_0():
    hdr = ag.file_list.header()
    ww = ag.file_list.width()
    sz = ww-6 if ag.file_list.verticalScrollBar().isVisible() else ww
    sz0 = sum((hdr.sectionSize(i) for i in range(1, hdr.count())))
    hdr.resizeSection(0, max(sz - sz0, min_width))

def file_list_resize_0(e: QResizeEvent):
    def file_list_resize(e: QResizeEvent):
        resize_section_0()
        super(QTreeView, ag.file_list).resizeEvent(e)

    if ag.db.conn:
        restore_dirs()

    ag.file_list.resizeEvent = file_list_resize

def set_field_menu():
    hdr = ag.file_list.header()

    menu = QMenu(ag.app)
    for i,field,tt in zip(range(len(low_bk.fields)), low_bk.fields, tool_tips):
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
    low_bk.set_dir_model()
    ag.filter_dlg.restore_filter_settings()
    restore_history()
    if ag.mode is ag.appMode.FILTER:
        low_bk.filtered_files()
        row = ag.get_setting("FILTER_FILE_ROW", 0)
        idx = ag.file_list.model().index(row, 0)
        ag.file_list.setCurrentIndex(idx)
        ag.file_list.scrollTo(idx)
    elif  ag.mode is ag.appMode.DIR:
        history_dir_files()
    elif  ag.mode is ag.appMode.HISTORY_FILES:
        low_bk.show_recent_files()
    else:   #  ag.appMode.FILTER_SETUP
        low_bk.show_files([])

    header_restore()
    set_field_menu()

def header_restore():
    hdr: QHeaderView = ag.file_list.header()
    try:
        state = ag.get_setting("FILE_LIST_HEADER")
        if state:
            hdr.restoreState(state)
    except Exception as e:
        logger.info(f'{type(e)}; {e.args}', exc_info=True)

    hdr.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
    hdr.sectionResized.connect(resized_column)

    hdr.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
    hdr.customContextMenuRequested.connect(header_menu)

@pyqtSlot(QPoint)
def header_menu(pos: QPoint):
    hdr: QHeaderView = ag.file_list.header()
    idx = hdr.logicalIndexAt(pos)
    if idx:
        me = QMenu()
        me.addAction(f'Hide column "{low_bk.fields[idx]}"')
        action = me.exec(hdr.mapToGlobal(
            QPoint(pos.x(), pos.y() + hdr.height()))
        )
        if action:
            toggle_show_column(False, idx)
            menu = ag.app.ui.field_menu.menu()
            menu.actions()[idx].setChecked(False)

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

    hide_state = ag.get_setting("SHOW_HIDDEN", 0)
    self.show_hidden.setChecked(hide_state)
    self.show_hidden.setIcon(tug.get_icon("show_hide", hide_state))
    ag.buttons.append((self.show_hidden, "show_hide"))

    ag.file_data.set_edit_state(
        ag.get_setting("NOTE_EDIT_STATE", (False,))
    )

def restore_history():
    ag.file_history = ag.get_setting('FILE_HISTORY', [])
    hist = ag.get_setting('DIR_HISTORY', [[], [], []])  # next_, prev, curr
    if not hist[2] and ag.dir_list.model().rowCount():
        idx = ag.dir_list.model().index(0, 0, QModelIndex())
        if idx.isValid():
            udat: ag.DirData = idx.data(Qt.ItemDataRole.UserRole)
            hist[2] = [udat.id,]
            ag.dir_list.setCurrentIndex(idx)

    low_bk.hist_folder = bool(hist[2])
    ag.history.set_history(*hist)

def history_dir_files():
    idx = low_bk.expand_branch(ag.history.get_current())
    if idx.isValid():
        ag.dir_list.setCurrentIndex(idx)
    else:
        low_bk.show_folder_files()

@pyqtSlot()
def refresh_dir_list():
    """
    QCheckBox stateChanged signal handler
    """
    branch = low_bk.define_branch(ag.dir_list.currentIndex())
    low_bk.set_dir_model()
    idx = low_bk.expand_branch(branch)

    ag.dir_list.setCurrentIndex(idx)

@pyqtSlot(QPoint)
def dir_menu(pos):
    idx = ag.dir_list.indexAt(pos)
    menu = QMenu(self)
    if idx.isValid():
        menu.addSeparator()
        menu.addAction("Delete folder(s)\tDel")
        menu.addSeparator()
        menu.addAction("Toggle hidden state")
        menu.addSeparator()
        menu.addAction("Edit tooltip")
        menu.addSeparator()
        menu.addAction("Import files")
        menu.addSeparator()
        menu.addAction("Create folder\tCtrl-W")
        menu.addAction("Create folder as child\tCtrl-E")
    else:
        menu.addAction("Create folder\tCtrl-W")

    action = menu.exec(ag.dir_list.mapToGlobal(pos))
    if action:
        item = action.text().split('\t')[0]
        ag.signals_.user_signal.emit(f"Dirs {item}")

@pyqtSlot(QPoint)
def file_menu(pos):
    idx = ag.file_list.indexAt(pos)
    if idx.isValid():
        menu = QMenu(self)
        menu.addAction("Copy file name(s)")
        menu.addAction("Copy full file name(s)")
        menu.addAction("Reveal in explorer")
        menu.addSeparator()
        menu.addAction("Open file")
        menu.addSeparator()
        menu.addAction("Rename file")
        menu.addSeparator()
        menu.addAction("Export selected files")
        menu.addSeparator()
        if ag.mode is ag.appMode.HISTORY_FILES:
            menu.addAction("Clear file history")
            menu.addAction("Remove selected from history")
        else:
            menu.addAction("Remove file(s) from folder")
        menu.addSeparator()
        menu.addAction("Delete file(s) from DB")
        action = menu.exec(ag.file_list.mapToGlobal(pos))
        if action:
            ag.signals_.user_signal.emit(f"Files {action.text()}")

@pyqtSlot(str, list)
def file_loading(root_path: str, ext: list[str]):
    """
    search for files with a given extension
    in the selected folder and its subfolders
    """
    if self.is_busy or not ag.db.conn:
        return
    self.thread = QThread(self)

    self.worker = load_files.loadFiles()
    self.worker.set_files_iterator(load_files.yield_files(root_path, ext))
    self.worker.moveToThread(self.thread)

    self.thread.started.connect(self.worker.load_data)
    self.worker.finished.connect(finish_loading)
    self.worker.finished.connect(self.worker.deleteLater)

    self.thread.start()
    self.set_busy(True)

@pyqtSlot(bool)
def finish_loading(has_new_ext: bool):
    self.thread.quit()
    self.set_busy(False)
    if has_new_ext:
        ag.signals_.user_signal.emit("ext inserted")
    low_bk.reload_dirs_changed(ag.dir_list.currentIndex())

@pyqtSlot()
def check_duplicates(auto=True):
    rep = workers.report_duplicates()
    if rep:
        dup_dlg = dup.dlgDup(rep, ag.app)
        dup_dlg.move(
            (ag.app.width()-dup_dlg.width()) // 3,
            (ag.app.height()-dup_dlg.height()) // 3
        )
        dup_dlg.asked_by_user(not auto)
        dup_dlg.show()
    elif not auto:
        ag.show_message_box(
            "No duplicates found",
            "No file duplicates found in DB"
        )

@pyqtSlot()
def show_lost_files():
    workers.find_lost_files()

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

@pyqtSlot()
def run_update_pdf_files():
    """
    collect specifict data about recently loaded pdf files
    """
    run_worker(workers.update_pdf_files)

def run_worker(func):
    if self.is_busy or not ag.db.conn:
        return
    self.thread = QThread(self)

    self.worker = workers.worker(func)
    self.worker.moveToThread(self.thread)

    self.thread.started.connect(self.worker.run)
    self.worker.finished.connect(finish_worker)
    self.worker.finished.connect(self.worker.deleteLater)

    self.thread.start()
    self.set_busy(True)

@pyqtSlot()
def finish_worker():
    self.thread.quit()
    self.set_busy(False)
