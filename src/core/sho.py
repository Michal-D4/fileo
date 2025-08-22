from loguru import logger
from pathlib import Path
import time

from PyQt6.QtCore import QPoint, Qt, pyqtSlot, QRect, QObject, QSize
from PyQt6.QtGui import (QCloseEvent, QEnterEvent, QMouseEvent,
    QResizeEvent, QKeySequence, QShortcut,
)
from PyQt6.QtWidgets import (QMainWindow, QToolButton, QAbstractItemView,
    QVBoxLayout, QTreeView, QFrame, QWidget,
)

from .. import tug
from .compact_list import aBrowser
from .filename_editor import fileEditorDelegate, folderEditDelegate
from ..ui.ui_main import Ui_Sho
from ..widgets.file_data import fileDataHolder
from ..widgets.filter_setup import FilterSetup
from ..widgets.fold_container import FoldContainer

from . import db_ut, bk_ut, history, low_bk, app_globals as ag
from .win_win import setup_ui, update_grips


MIN_NOTE_HEIGHT = 75
MIN_CONTAINER_WIDTH = 135
DEFAULT_CONTAINER_WIDTH = 170
DEFAULT_HISTORY_DEPTH = 15

def set_widget_to_frame(frame: QFrame, widget: QWidget):
    frame.setLayout(QVBoxLayout())
    frame.layout().setContentsMargins(0,0,0,0)
    frame.layout().addWidget(widget)


class shoWindow(QMainWindow):
    def __init__(self, db_name: str, first_instance: bool, parent = None) -> None:
        super().__init__(parent)
        self.first_instance = first_instance
        self.loader: QObject = None

        self.ui = Ui_Sho()
        self.ui.setupUi(self)
        self.ui.ico.setPixmap(tug.get_icon('ico_app').pixmap(24, 24))

        self.create_fold_container()

        self.start_pos: QPoint = QPoint()

        self.connect_slots()
        self.set_extra_buttons()

        self.setup_global_widgets()
        self.set_button_icons()
        self.restore_settings(db_name)
        bk_ut.bk_setup()
        self.set_busy(False)
        bk_ut.set_files_resize_event()

    def create_fold_container(self):
        fold_layout = QVBoxLayout(self.ui.left_pane)
        fold_layout.setContentsMargins(0, 0, 0, 0)
        fold_layout.setSpacing(0)
        self.container = FoldContainer(self.ui.left_pane)
        fold_layout.addWidget(self.container)

    def tune_app_version(self):
        """
        make changes to "setting" if necessary
        """
        cur_v = ag.app_version()
        cur_v = int(cur_v.replace('.', ''))
        saved_v = ag.get_db_setting("AppVersion", 0)

        if saved_v == cur_v:
            return

        def ver1348():
            if saved_v < 1348:
                path = tug.get_app_setting('DEFAULT_FILE_PATH',
                    str(Path('~/fileo/files').expanduser()))
                if not Path(path).exists():
                    tug.create_dir(Path(path))
                    tug.save_app_setting(DEFAULT_FILE_PATH=path)

        ver1348()

        ag.save_db_settings(AppVersion=cur_v)

    def restore_settings(self, db_name: str):
        ag.signals_.user_signal.connect(low_bk.set_user_action_handlers())
        ag.signals_.author_widget_title.connect(self.change_menu_more)

        self.restore_geometry()
        self.restore_container()
        self.restore_note_height()

        ag.file_data = fileDataHolder()
        ag.file_data.setObjectName("file_data_holder")
        set_widget_to_frame(self.ui.noteHolder, ag.file_data)
        ag.history = history.History(
            int(tug.get_app_setting('FOLDER_HISTORY_DEPTH', DEFAULT_HISTORY_DEPTH))
        )

        low_bk.init_db(
            tug.get_app_setting("DB_NAME", "")
            if self.first_instance else db_name
        )

    def set_busy(self, val: bool):
        self.is_busy = val
        pix = tug.get_icon("busy", int(val))
        self.ui.busy.setPixmap(pix.pixmap(16, 16))
        self.ui.busy.setToolTip(
            'Background thread is working' if val else 'No active background thread'
        )

    def connect_db(self, path: str) -> bool:
        logger.info(f'open DB: {Path(path).name}')
        if db_ut.create_connection(path):
            self.ui.db_name.setText(Path(path).name)
            self.init_filter_setup()
            ag.file_data.set_tag_author_data()
            return True
        self.ui.db_name.setText('Click to select DB')
        return False

    def restore_container(self):
        self.ui.field_menu.setIcon(tug.get_icon("more"))
        ag.buttons.append((self.ui.field_menu, "more"))
        bk_ut.set_menu_more(self)

        state = tug.get_app_setting("container", (DEFAULT_CONTAINER_WIDTH, None))
        if state:
            self.container.restore_state(state[1:])
            menu = self.ui.more.menu()
            for i, ff in enumerate(ag.fold_grips):
                menu.actions()[i].setChecked(not ff.is_hidden)
            self.ui.left_pane.setMinimumWidth(int(state[0]))

    def restore_mode(self):
        mode = ag.appMode(
            int(ag.get_db_setting("APP_MODE", ag.appMode.DIR.value))
        )
        if mode.value > ag.appMode.RECENT_FILES.value:
            mode = ag.appMode.DIR
        btn = self.ui.toolbar_btns.button(mode.value)
        btn.setChecked(True)
        ag.set_mode(mode)
        self.toggle_filter_show()

    def restore_note_height(self):
        hh = tug.get_app_setting("noteHolderHeight", MIN_NOTE_HEIGHT)
        self.ui.noteHolder.setMinimumHeight(int(hh))
        self.ui.noteHolder.setMaximumHeight(int(hh))

    def restore_geometry(self):
        self.rect = tug.get_app_setting("MainWindowGeometry")
        if isinstance(self.rect, QRect):
            self.setGeometry(self.rect)
            if not self.first_instance:
                self.move(self.x() + 40, self.y() + 40)

        setup_ui(self)

    def sizeHint(self):
        return QSize(self.rect.width(), self.rect.height())

    def set_extra_buttons(self):
        self.btn_prev = self._create_button("prev_folder", 'btn_prev', 'Prev folder')
        self.btn_prev.setPopupMode(QToolButton.ToolButtonPopupMode.DelayedPopup)
        self.btn_prev.clicked.connect(low_bk.to_prev_folder)
        self.btn_prev.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.btn_prev.customContextMenuRequested.connect(lambda pos, btn=self.btn_prev: low_bk.show_history_menu(pos, btn))
        self.btn_prev.setDisabled(True)

        self.btn_next = self._create_button("next_folder", 'btn_next', 'Next folder')
        self.btn_next.setPopupMode(QToolButton.ToolButtonPopupMode.DelayedPopup)
        self.btn_next.clicked.connect(low_bk.to_next_folder)
        self.btn_next.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.btn_next.customContextMenuRequested.connect(lambda pos, btn=self.btn_next: low_bk.show_history_menu(pos, btn))
        self.btn_next.setDisabled(True)

        self.refresh_tree = self._create_button("refresh", 'refresh', 'Refresh folder list')
        self.refresh_tree.clicked.connect(low_bk.refresh_dir_list)
        self.refresh_tree.setDisabled(True)

        self.show_hidden = self._create_button("show_hide", 'show_hide', 'Show hidden folders')
        self.show_hidden.setCheckable(True)
        self.show_hidden.clicked.connect(self.show_hide_click)
        self.show_hidden.setDisabled(True)

        self.collapse_btn = self._create_button("collapse_all", 'collapse_all', 'Collapse/expand tree')
        self.collapse_btn.setCheckable(True)
        self.collapse_btn.clicked.connect(bk_ut.toggle_collapse)
        self.collapse_btn.setDisabled(True)

    def _create_button(self, icon_name: str, btn_name: str, tool_tip: str) -> QToolButton:
        btn = QToolButton()
        btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        btn.setStyleSheet("border:none; margin:0px; padding:0px;")
        btn.setAutoRaise(True)
        btn.setIcon(tug.get_icon(icon_name))
        ag.buttons.append((btn, icon_name))
        btn.setObjectName(btn_name)
        self.container.add_widget(btn, 0)
        btn.setToolTip(tool_tip)
        return btn

    @pyqtSlot(bool)
    def show_hide_click(self, state: bool):
        low_bk.refresh_dir_list()
        self.show_hidden.setIcon(tug.get_icon("show_hide", int(state)))

    def setup_global_widgets(self):
        frames = self.container.get_frames()

        ag.dir_list = QTreeView()
        ag.dir_list.setDragEnabled(True)
        ag.dir_list.setAcceptDrops(True)
        ag.dir_list.setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)
        ag.dir_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        ag.dir_list.setObjectName('dir_list')
        ag.dir_list.expanded.connect(lambda: self.collapse_btn.setChecked(False))
        set_widget_to_frame(frames[0], ag.dir_list)
        ag.dir_list.focusInEvent = low_bk.dirlist_get_focus
        ag.dir_list.setItemDelegateForColumn(0, folderEditDelegate(self))

        ag.tag_list = aBrowser(read_only=False)
        ag.tag_list.setObjectName("tag_list")
        set_widget_to_frame(frames[1], ag.tag_list)

        ag.ext_list = aBrowser(brackets=True)
        ag.ext_list.setObjectName("ext_list")
        set_widget_to_frame(frames[2], ag.ext_list)

        ag.author_list = aBrowser(read_only=False, brackets=True)
        ag.author_list.setObjectName("author_list")
        set_widget_to_frame(frames[3], ag.author_list)

        ag.file_list = self.ui.file_list
        ag.file_list.setItemDelegateForColumn(0, fileEditorDelegate(self))

        self.ui.btn_search.setIcon(tug.get_icon("search"))
        ag.buttons.append((self.ui.btn_search, "search"))
        self.ui.btn_search.clicked.connect(bk_ut.search_files)
        ctrl_f = QShortcut(QKeySequence("Ctrl+F"), ag.file_list)
        ctrl_f.setContext(Qt.ShortcutContext.WidgetShortcut)
        ctrl_f.activated.connect(bk_ut.search_files)
        self.ui.btn_search.setDisabled(True)

        self.ui.recent_files.setIcon(tug.get_icon("history"))
        ag.buttons.append((self.ui.recent_files, "history"))
        self.ui.recent_files.clicked.connect(low_bk.show_recent_files)
        self.ui.recent_files.setShortcut(QKeySequence("Ctrl+H"))

        ctrl_n = QShortcut(QKeySequence("Ctrl+N"), ag.file_list)
        ctrl_n.setContext(Qt.ShortcutContext.WidgetShortcut)
        ctrl_n.activated.connect(lambda: ag.signals_.user_signal.emit("Files Create new file"))

    def set_button_icons(self):
        m_icons = [
            "btnDir", "btnFilter", "btnFilterSetup",
            "btnToggleBar", "btnSetup", 'minimize', 'maximize', 'close'
        ]
        self.ui.toolbar_btns.setId(self.ui.btnDir, ag.appMode.DIR.value)
        self.ui.toolbar_btns.setId(self.ui.btnFilter, ag.appMode.FILTER.value)
        self.ui.toolbar_btns.setId(self.ui.btnFilterSetup, ag.appMode.FILTER_SETUP.value)
        for icon_name in m_icons:
            btn: QToolButton  = getattr(self.ui, icon_name)
            btn.setIcon(tug.get_icon(icon_name, int(btn.isChecked())))
            ag.buttons.append((btn, icon_name))

    def change_menu_more(self, new_ttl: str):
        menu = self.ui.more.menu()
        menu.actions()[-1].setText(new_ttl)

    def connect_slots(self):
        ag.app = bk_ut.self = self
        self.ui.toolbar_btns.idClicked.connect(self.toggle_btn)

        self.ui.btnToggleBar.clicked.connect(self.click_toggle_bar)
        self.ui.btnToggleBar.setShortcut(QKeySequence("Ctrl+B"))
        self.ui.btnSetup.clicked.connect(bk_ut.show_main_menu)

        self.ui.db_name.mousePressEvent = self.db_list_show

        self.ui.vSplit.enterEvent = self.vsplit_enter_event
        self.ui.vSplit.mousePressEvent = self.vsplit_press_event
        self.ui.vSplit.mouseMoveEvent = self.vsplit_move_event
        self.ui.vSplit.leaveEvent = self.leave_event

        self.ui.hSplit.enterEvent = self.hsplit_enter_event
        self.ui.hSplit.mousePressEvent = self.hsplit_press_event
        self.ui.hSplit.mouseMoveEvent = self.hsplit_move_event
        self.ui.hSplit.leaveEvent = self.leave_event

        ag.signals_.open_db_signal.connect(self.switch_db)
        ag.signals_.filter_setup_closed.connect(self.close_filter_setup)

    def toggle_btn(self, id: int):
        logger.info(f'{id=}, {ag.appMode(id).name=}')
        if id == ag.curr_btn_id:
            return
        ag.set_mode(ag.appMode(id))
        self.toggle_filter_show()
        low_bk.refresh_file_list()

    def db_list_show(self, e: QMouseEvent):
        if e.buttons() == Qt.MouseButton.LeftButton:
            ag.signals_.user_signal.emit("MainMenu DB selector")

    @pyqtSlot()
    def close_filter_setup(self):
        self.ui.btnFilter.setChecked(True)
        ag.set_mode(ag.appMode.FILTER)
        low_bk.filtered_files()

    @pyqtSlot(str)
    def switch_db(self, db_name: str):
        if db_name == ag.db.path:
            return

        bk_ut.save_bk_settings()
        if self.connect_db(db_name):
            self.tune_app_version()
            self.restore_mode()
            bk_ut.populate_all()
            bk_ut.restore_dirs()

    @pyqtSlot(QMouseEvent)
    def hsplit_enter_event(self, e: QEnterEvent):
        self.setCursor(Qt.CursorShape.SizeVerCursor)
        e.accept()

    @pyqtSlot(QMouseEvent)
    def hsplit_press_event(self, e: QMouseEvent):
        cur_pos = e.globalPosition().toPoint()
        self.start_pos = self.mapFromGlobal(cur_pos)
        e.accept()

    @pyqtSlot(QMouseEvent)
    def hsplit_move_event(self, e: QMouseEvent):
        if e.buttons() == Qt.MouseButton.LeftButton:
            cur_pos = e.globalPosition().toPoint()
            if not self.start_pos:
                self.start_pos = self.mapFromGlobal(cur_pos)
                return
            cur_pos = self.mapFromGlobal(cur_pos)

            self.setUpdatesEnabled(False)
            y: int = self.note_holder_resize(cur_pos.y())
            self.setUpdatesEnabled(True)

            self.start_pos.setY(y)
            e.accept()

    def note_holder_resize(self, y: int) -> int:
        y0 = self.start_pos.y()
        delta = y0 - y
        cur_height = self.ui.noteHolder.height()
        h = max(cur_height + delta, MIN_NOTE_HEIGHT)
        h = min(h, self.ui.main_pane.height() - MIN_NOTE_HEIGHT - 35)
        self.ui.noteHolder.setMinimumHeight(h)
        self.ui.noteHolder.setMaximumHeight(h)

        self.start_pos.setY(y0 - h + cur_height)
        return self.start_pos.y()

    @pyqtSlot(QMouseEvent)
    def vsplit_enter_event(self, e: QEnterEvent):
        self.setCursor(Qt.CursorShape.SizeHorCursor)
        e.accept()

    @pyqtSlot(QMouseEvent)
    def vsplit_press_event(self, e: QMouseEvent):
        cur_pos = e.globalPosition().toPoint()
        self.start_pos: QPoint = self.mapFromGlobal(cur_pos)
        e.accept()

    @pyqtSlot(QMouseEvent)
    def vsplit_move_event(self, e: QMouseEvent):
        if e.buttons() == Qt.MouseButton.LeftButton:
            cur_pos = e.globalPosition().toPoint()
            if not self.start_pos:
                self.start_pos = self.mapFromGlobal(cur_pos)
                return
            cur_pos = self.mapFromGlobal(cur_pos)

            self.setUpdatesEnabled(False)
            x: int = self.navigator_resize(cur_pos.x())
            self.setUpdatesEnabled(True)

            self.start_pos.setX(x)
            e.accept()

    def navigator_resize(self, x: int) -> int:
        x0 = self.start_pos.x()
        delta = x - x0
        cur_width = self.ui.left_pane.width()
        w = max(cur_width + delta, MIN_CONTAINER_WIDTH)
        w = min(w, (self.ui.main_pane.width() + cur_width) // 2)

        self.ui.left_pane.setMinimumWidth(w)

        self.start_pos.setX(x0 + w)
        return self.ui.left_pane.x() + w

    def leave_event(self, e):
        self.unsetCursor()
        self.start_pos = QPoint()

    def close_app(self):
        if self.is_busy:
            ag.stop_thread = True
            time.sleep(0.1)
        self.close()

    def toggle_filter_show(self):
        if not ag.db.conn:
            return
        def show_filter():
            pos_: QPoint = tug.get_app_setting("filterDialogPosition",
                QPoint(self.width() - ag.filter_dlg.width() - 10, 32))

            if pos_.x() < 0:
                pos_.setX(15)
            if pos_.y() < 0:
                pos_.setY(15)
            if pos_.x() > self.width() - ag.filter_dlg.width() + 30:
                pos_.setX(self.width() - ag.filter_dlg.width() - 15)
            if pos_.y() > self.height() - ag.filter_dlg.height() + 30:
                pos_.setY(self.height() - ag.filter_dlg.height() - 15)

            ag.filter_dlg.move(pos_)
            ag.filter_dlg.show()

        if self.ui.btnFilterSetup.isChecked():
            show_filter()
        elif ag.filter_dlg:
            if ag.filter_dlg.isVisible():
                tug.save_app_setting(filterDialogPosition = ag.filter_dlg.pos())
            ag.filter_dlg.hide()

    def init_filter_setup(self):
        ag.filter_dlg = FilterSetup(self)
        ag.tag_list.change_selection.connect(ag.filter_dlg.tag_selection_changed)
        ag.ext_list.change_selection.connect(ag.filter_dlg.ext_selection_changed)
        ag.author_list.change_selection.connect(ag.filter_dlg.author_selection_changed)

    @pyqtSlot()
    def click_toggle_bar(self):
        visible = self.ui.left_pane.isVisible()
        self.ui.left_pane.setVisible(not visible)
        self.ui.app_mode.setVisible(not visible)
        self.ui.more.setVisible(not visible)
        self.ui.btnToggleBar.setIcon(
            tug.get_icon("btnToggleBar", int(visible))
        )

    def resizeEvent(self, e: QResizeEvent) -> None:
        update_grips(self)
        super().resizeEvent(e)

    def closeEvent(self, event: QCloseEvent) -> None:
        settings = {
            "maximizedWindow": int(self.isMaximized()),
            "MainWindowGeometry": self.normalGeometry(),
            "container": self.container.save_state(),
            "noteHolderHeight": self.ui.noteHolder.height(),
            "DB_NAME": ag.db.path,
        }
        if ag.filter_dlg and ag.filter_dlg.isVisible():
            settings['filterDialogPosition'] = ag.filter_dlg.pos()

        if ag.db.conn:
            low_bk.save_db_list_at_close()
            settings["FILE_LIST_HEADER"] = ag.file_list.header().saveState()

        tug.save_app_setting(**settings)
        bk_ut.save_bk_settings()

        super().closeEvent(event)
