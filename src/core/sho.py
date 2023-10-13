from loguru import logger
from pathlib import Path
import sys
import time

from PyQt6.QtCore import QPoint, Qt, pyqtSlot
from PyQt6.QtGui import (QCloseEvent, QEnterEvent, QMouseEvent,
                         QResizeEvent, QPixmap,
)
from PyQt6.QtWidgets import (QMainWindow, QToolButton, QAbstractItemView,
                             QVBoxLayout, QTreeView, QVBoxLayout,
                             QFrame, QWidget,
)

from ..ui.ui_main import Ui_Sho
from ..widgets.file_data import fileDataHolder
from ..widgets.file_search import fileSearch
from ..widgets.filter_setup import FilterSetup
from ..widgets.fold_container import FoldContainer
from ..widgets.open_db import OpenDB

from .compact_list import aBrowser
from ..widgets.custom_grips import CustomGrip
from .filename_editor import fileEditorDelegate
from . import (icons, utils, db_ut, bk_ut, history, low_bk,
    app_globals as ag, iman,
)
if sys.platform.startswith("win"):
    from .win_win import setup_ui
elif sys.platform.startswith("linux"):
    from .linux_win import setup_ui, resize_grips
else:
    raise ImportError(f"doesn't support {sys.platform} system")



MIN_NOTE_HEIGHT = 75
MIN_CONTAINER_WIDTH = 135
DEFAULT_CONTAINER_WIDTH = 170
MAX_WIDTH_DB_DIALOG = 400
DEFAULT_HISTORY_DEPTH = 15

def set_widget_to_frame(frame: QFrame, widget: QWidget):
    frame.setLayout(QVBoxLayout())
    frame.layout().setContentsMargins(0,0,0,0)
    frame.layout().addWidget(widget)


class shoWindow(QMainWindow):
    def __init__(self, parent = None) -> None:
        super().__init__(parent)

        self.ui = Ui_Sho()

        self.ui.setupUi(self)
        self.create_fold_container()

        self.start_pos: QPoint = QPoint()
        self.start_move = QPoint()
        self.window_maximized: bool = False
        self.mode = ag.appMode.DIR
        self.open_db: OpenDB|None = None
        self.filter_setup: FilterSetup|None = None

        self.icons = icons.get_toolbar_icons()
        self.set_button_icons()
        self.connect_slots()
        self.set_extra_widgets()

        self.setup_global_widgets()
        self.restore_settings()
        self.restore_mode()
        bk_ut.bk_setup(self)
        self.set_busy(False)

    def create_fold_container(self):
        self.fold_layout = QVBoxLayout(self.ui.container)
        self.fold_layout.setContentsMargins(0, 0, 0, 0)
        self.fold_layout.setSpacing(0)
        self.container = FoldContainer(self.ui.container)
        self.fold_layout.addWidget(self.container)
        self.container.set_qss_fold(ag.dyn_qss['decorator'])

    def restore_settings(self):
        exec_user_action = low_bk.set_user_actions_handler()
        ag.signals_.user_signal.connect(exec_user_action)

        self.restore_geometry()
        self.restore_container()
        self.restore_note_height()

        ag.file_data_holder = fileDataHolder()
        ag.file_data_holder.setObjectName("file_notes")
        set_widget_to_frame(self.ui.noteHolder, ag.file_data_holder)
        ag.history = history.History(
            int(utils.get_app_setting('FOLDER_HISTORY_DEPTH', DEFAULT_HISTORY_DEPTH))
        )

        if ag.db.restore:     # start app with restoring DB connection - 1st app instance
            self.connect_db(
                ag.db.path or str(utils.get_app_setting("DB_NAME", ""))
            )

    def set_busy(self, val: bool):
        self.is_busy = val
        self.ui.busy.setPixmap(QPixmap(icons.get_other_icon("busy", int(val))))
        self.ui.busy.setToolTip(
            'Background thread is working' if val else 'No active background thread'
        )

    def connect_db(self, path: str) -> bool:
        if db_ut.create_connection(path):
            self.ui.db_name.setText(Path(path).name)
            self.init_filter_setup()
            bk_ut.set_field_menu()
            ag.file_data_holder.set_tag_author_data()
            return True
        return False

    def restore_container(self):
        state = utils.get_app_setting("container", (DEFAULT_CONTAINER_WIDTH, None))
        if state:
            self.container.restore_state(state[1:])
            self.ui.container.setMinimumWidth(int(state[0]))

    def restore_mode(self):
        self.mode = ag.appMode(
            int(utils.get_app_setting("appMode", ag.appMode.DIR.value))
        )
        self.click_checkable_button(True, self.mode)

    def restore_note_height(self):
        hh = utils.get_app_setting("noteHolderHeight", MIN_NOTE_HEIGHT)
        self.ui.noteHolder.setMinimumHeight(int(hh))
        self.ui.noteHolder.setMaximumHeight(int(hh))

    def restore_geometry(self):
        geometry = utils.get_app_setting("MainWindowGeometry")

        if geometry:
            self.restoreGeometry(geometry)
            logger.info(self.geometry())

        setup_ui(self)

    @property
    def mode(self) -> int:
        return ag.mode

    @mode.setter
    def mode(self, val: ag.appMode):
        ag.mode = val
        self.container.ui.app_mode.setText(f"{val}")

    def set_extra_widgets(self):
        self.btn_prev = self._create_button("prev_folder", 'btn_prev', 'Previous folder')
        self.btn_prev.clicked.connect(low_bk.to_prev_folder)
        self.btn_prev.setDisabled(True)

        self.btn_next = self._create_button("next_folder", 'btn_next', 'Next folder')
        self.btn_next.clicked.connect(low_bk.to_next_folder)
        self.btn_next.setDisabled(True)

        self.refresh_tree = self._create_button("refresh", 'refresh', 'Refresh folder list')
        self.refresh_tree.clicked.connect(bk_ut.show_hidden_dirs)
        self.refresh_tree.setDisabled(True)

        self.show_hidden = self._create_button("show_hide", 'show_hide', 'Show hidden folders')
        self.show_hidden.setCheckable(True)
        self.show_hidden.clicked.connect(self.show_hide_click)
        self.show_hidden.setDisabled(True)

        self.collapse_btn = self._create_button("collapse_all", 'collapse_all', 'Collapse/expand tree')
        self.collapse_btn.setCheckable(True)
        self.collapse_btn.clicked.connect(bk_ut.toggle_collapse)
        self.collapse_btn.setDisabled(True)

    def _create_button(self, icon_name: str, o_name: str, tool_tip: str) -> QToolButton:
        btn = QToolButton()
        btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        btn.setStyleSheet("border:0px; margin:0px; padding:0px;")
        btn.setAutoRaise(True)
        btn.setIcon(icons.get_other_icon(icon_name))
        btn.setObjectName(o_name)
        self.container.add_widget(btn, 0)
        btn.setToolTip(tool_tip)
        return btn

    @pyqtSlot(bool)
    def show_hide_click(self, state: bool):
        bk_ut.show_hidden_dirs()
        self.show_hidden.setIcon(icons.get_other_icon("show_hide", int(state)))

    def setup_global_widgets(self):
        ag.app = bk_ut.self = self

        frames = self.container.get_widgets()

        ag.dir_list = QTreeView()
        ag.dir_list.setObjectName("dir_list")
        ag.dir_list.setDragEnabled(True)
        ag.dir_list.setAcceptDrops(True)
        ag.dir_list.setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)
        ag.dir_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        ag.dir_list.setFocusPolicy(Qt.FocusPolicy.StrongFocus) # default
        ag.dir_list.setObjectName('dir_list')
        ag.dir_list.expanded.connect(self.branch_expanded)
        set_widget_to_frame(frames[0], ag.dir_list)

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
        ag.file_list.setItemDelegateForColumn(0, fileEditorDelegate(ag.file_list))
        ag.field_menu = self.ui.field_menu

    @pyqtSlot()
    def branch_expanded(self):
        self.collapse_btn.setChecked(False)

    def set_button_icons(self):
        for btn_name, icon in self.icons.items():
            btn: QToolButton  = getattr(self.ui, btn_name)
            btn.setIcon(icon[btn.isChecked()])
        self.ui.btn_search.setIcon(icons.get_other_icon("search"))
        self.ui.btn_search.clicked.connect(bk_ut.search_files)
        self.ui.btn_search.setDisabled(True)

    def connect_slots(self):
        self.connect_checkable()


        self.ui.dataBase.clicked.connect(self.show_db_list)

        self.ui.btnScan.clicked.connect(self.click_scan)
        self.ui.btnToggleBar.clicked.connect(self.click_toggle_bar)
        self.ui.btnSetup.clicked.connect(bk_ut.click_setup_button)

        self.ui.vSplit.enterEvent = self.vsplit_enter_event
        self.ui.vSplit.mousePressEvent = self.vsplit_press_event
        self.ui.vSplit.mouseMoveEvent = self.vsplit_move_event
        self.ui.vSplit.leaveEvent = self.leave_event

        self.ui.hSplit.enterEvent = self.hsplit_enter_event
        self.ui.hSplit.mousePressEvent = self.hsplit_press_event
        self.ui.hSplit.mouseMoveEvent = self.hsplit_move_event
        self.ui.hSplit.leaveEvent = self.leave_event

        ag.signals_.get_db_name.connect(self.get_db_name)
        ag.signals_.filter_setup_closed.connect(self.close_filter_setup)

    @pyqtSlot()
    def close_filter_setup(self):
        self.mode = ag.appMode.FILTER
        self.click_checkable_button(True, self.mode)

    @pyqtSlot(str)
    def get_db_name(self, db_name: str):
        if db_name == ag.db.path:
            return

        bk_ut.save_bk_settings()
        if self.connect_db(db_name):
            bk_ut.populate_all()
            bk_ut.restore_dirs()

    @pyqtSlot()
    def show_db_list(self):
        """
        manage the list of sqlite db files
        and choose which to use
        """
        if not self.open_db:
            self.open_db = OpenDB(self)
        self.open_db.move(48, 20)
        self.open_db.resize(min(self.width() // 2, MAX_WIDTH_DB_DIALOG),
            self.height() - 60)
        self.open_db.show()

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
        h = min(h, self.ui.fileFrame.height() - MIN_NOTE_HEIGHT - 35)
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
        cur_width = self.ui.container.width()
        w = max(cur_width + delta, MIN_CONTAINER_WIDTH)
        w = min(w, (self.ui.fileFrame.width() + cur_width) // 2)

        self.ui.container.setMinimumWidth(w)

        self.start_pos.setX(x0 + w)
        return self.ui.container.x() + w

    def leave_event(self, e):
        self.unsetCursor()
        self.start_pos = None

    def connect_checkable(self):
        self.checkable_btn = {
            ag.appMode.DIR: self.ui.btnDir,
            ag.appMode.FILTER: self.ui.btnFilter,
            ag.appMode.FILTER_SETUP: self.ui.btnFilterSetup,
        }

        for key, btn in self.checkable_btn.items():
            btn.clicked.connect(lambda state, bc=key:
                self.click_checkable_button(state, bt_key=bc))

    def minimize(self):
        self.showMinimized()

    def close_app(self):
        if self.is_busy:
            ag.stop_thread = True
            time.sleep(0.1)
        self.close()

    def click_checkable_button(self, state: bool, bt_key: ag.appMode):
        """
        state = True if clicked button checked
        bt_key - here the key of checkable_btn dict
        there are three checkable buttons on left tool bar:
        btnDir, btnFilter, btnFilterSetup
        click button changes state of application
        change icon of checkable button depending on its state
        """
        old_mode = ag.mode.value
        if state:
            # need loop to find button to upcheck
            for key, btn in self.checkable_btn.items():
                btn.setIcon(self.icons[btn.objectName()][key is bt_key])
        else:
            self.checkable_btn[bt_key].setIcon[bt_key][0]

        self.mode = bt_key
        self.checkable_btn[self.mode].setChecked(True)
        ag.signals_.app_mode_changed.emit(old_mode)

        self.toggle_filter_show()

    def toggle_filter_show(self):
        if not ag.db.conn:
            return
        if self.ui.btnFilterSetup.isChecked():
            self.filter_setup.move(self.width() - self.filter_setup.width() - 10, 32)
            self.filter_setup.show()
        elif self.filter_setup:
            self.filter_setup.hide()

    def init_filter_setup(self):
        self.filter_setup = FilterSetup(self)
        ag.tag_list.change_selection.connect(self.filter_setup.tag_selection_changed)
        ag.ext_list.change_selection.connect(self.filter_setup.ext_selection_changed)
        ag.author_list.change_selection.connect(self.filter_setup.author_selection_changed)
        ag.filter_dlg = self.filter_setup

    @pyqtSlot()
    def click_scan(self):
        """
        search for files with a given extension
        in the selected folder and its subfolders
        """
        if not ag.db.conn:
            return
        srch_files = fileSearch(self)
        srch_files.move(
            (self.width()-srch_files.width()) // 4,
            (self.height()-srch_files.height()) // 4)
        srch_files.show()
        self.ui.btnScan.setEnabled(False)

    @pyqtSlot()
    def click_toggle_bar(self):
        if self.ui.container.isVisible():
            self.ui.container.hide()
            self.ui.btnToggleBar.setIcon(self.icons["btnToggleBar"][1])
        else:
            self.ui.container.show()
            self.ui.btnToggleBar.setIcon(self.icons["btnToggleBar"][0])

    # def mousePressEvent(self, e: QMouseEvent):
    #     if self.open_db and self.open_db.isVisible():
    #         # close dialog when mouse is pressed outside of it
    #         ag.signals_.close_db_dialog.emit()
    #     self.start_move = e.globalPosition().toPoint()
    #     e.accept()

    def resizeEvent(self, e: QResizeEvent) -> None:
        o = e.oldSize()
        s = e.size()
        logger.info(f'x: ({s.width()} - {o.width()}), y: ({s.height()} - {o.height()})')
        for grip in self.grips.values():
            grip.update_grip()
        if self.filter_setup and self.filter_setup.isVisible():
            self.filter_setup.move(self.width() - self.filter_setup.width() - 10, 32)
        super().resizeEvent(e)
        e.accept()

    def closeEvent(self, event: QCloseEvent) -> None:
        logger.info('<<<<<<<')
        iman.app_instance_closed()
        settings = {
            "maximizedWindow": int(self.window_maximized),
            "MainWindowGeometry": self.saveGeometry(),
            "container": self.container.save_state(),
            "appMode": self.mode.value,
            "noteHolderHeight": self.ui.noteHolder.height(),
        }
        if ag.db.path:
            settings["DB_NAME"] = ag.db.path

        utils.save_app_setting(**settings)
        bk_ut.save_bk_settings()

        super().closeEvent(event)
