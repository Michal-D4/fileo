from loguru import logger
from pathlib import Path
from datetime import datetime

from PyQt6.QtCore import Qt, pyqtSlot, QPoint
from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtWidgets import (QFileDialog, QMenu,
    QTableWidgetItem, QWidget, QMessageBox,
    QHeaderView, QStyle,
)

from .cust_msgbox import show_message_box
from ..core import create_db, app_globals as ag
from .ui_open_db import Ui_openDB
from .. import tug

TIME_0 = datetime(1, 1, 1)

class OpenDB(QWidget, Ui_openDB):

    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)

        self.setupUi(self)
        self.msg = ''

        self.restore_db_list()
        self.listDB.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.listDB.itemEntered.connect(self.item_enter)
        self.listDB.itemClicked.connect(self.item_click)
        self.listDB.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.listDB.customContextMenuRequested.connect(self.item_menu)
        self.listDB.setCurrentCell(0, 0)
        self.btn_add.setIcon(tug.get_icon("plus"))
        self.btn_add.clicked.connect(lambda: ag.signals.user_signal.emit("MainMenu Create/Open DB"))

        return_key = QShortcut(QKeySequence(Qt.Key.Key_Return), self)
        return_key.activated.connect(lambda: self.item_click(self.listDB.currentItem()))

        ag.popups["OpenDB"] = self

    @pyqtSlot(QTableWidgetItem)
    def item_enter(self, item: QTableWidgetItem):
        self.listDB.selectRow(item.row())

    @pyqtSlot(QPoint)
    def item_menu(self, pos: QPoint):
        item: QTableWidgetItem = self.listDB.itemAt(pos)
        if item:
            if item.column() > 0:
                item = self.listDB.item(item.row(), 0)
            path, used, _ = item.data(Qt.ItemDataRole.UserRole)
            db_path = Path(path)
            menu = self.db_list_menu(db_path.name, used)
            action = menu.exec(self.listDB.mapToGlobal(pos))
            if action:
                menu_item_text = action.text()
                if not used and menu_item_text.endswith('window'):
                    self.open_in_new_window(str(db_path))
                elif not used and menu_item_text.startswith('Delete'):
                    self.remove_row(item.row())
                elif menu_item_text.startswith('Open'):
                    self.check_and_open(str(db_path), used)
                elif menu_item_text.startswith('Reveal'):
                    tug.reveal_file(str(db_path))
                elif menu_item_text.startswith('Free'):
                    self.mark_not_used(item.row())

    def db_list_menu(self, db_name: str, used: bool) -> QMenu:
        menu = QMenu(self)
        menu.addAction(f'Open DB "{db_name}"')
        menu.addSeparator()
        menu.addAction(f'Open DB "{db_name}" in new window')
        menu.addSeparator()
        menu.addAction(f'Reveal "{db_name}" in explorer')
        menu.addSeparator()
        menu.addAction(f'Delete DB "{db_name}" from list')
        if used and not ag.db.path.endswith(db_name):
            menu.addSeparator()
            menu.addAction(f'Free DB "{db_name}"')
        return menu

    def restore_db_list(self):
        db_list = tug.get_app_setting("DB_List", [])

        for ii, row in enumerate(db_list):
            path, used, last_dt = row
            self.set_cell_0(path, used, last_dt, ii)
            self.listDB.setItem(ii, 1, QTableWidgetItem(f'{("Now" if used else last_dt)!s}'))

    def set_cell_0(self, path: str, used: bool, dt: str, row: int=0):
        self.listDB.insertRow(row)
        item0 = QTableWidgetItem()
        item0.setData(Qt.ItemDataRole.DisplayRole, Path(path).name)
        item0.setData(Qt.ItemDataRole.UserRole, (path, used, dt))
        self.listDB.setItem(row, 0, item0)

    def remove_row(self, row: int):
        self.listDB.removeRow(row)
        db_list = self.get_item_list()
        tug.save_app_setting(DB_List=db_list)

    def add_db_name(self, db_path:str):
        if self.open_existed(db_path):
            return

        self.open_if_ok(db_path)

    def open_if_ok(self, db_path: str):
        if self.verify_db_file(db_path):
            now = str(datetime.now().replace(microsecond=0))
            self.set_cell_0(db_path, True, now)
            self.open_db(db_path)
            return
        logger.info(f'{self.msg=}')
        show_message_box('Error open DB', self.msg,
            icon=QStyle.StandardPixmap.SP_MessageBoxCritical
        )

    def open_existed(self, db_path: str) -> bool:
        for item, used, _ in self.get_item_list():
            if item == db_path:
                return self.check_and_open(db_path, used)
        return False

    def add_db(self):
        pp = Path('~/fileo/dbs').expanduser()
        path = tug.get_app_setting('DEFAULT_DB_PATH', str(pp))
        db_name, ok_ = QFileDialog.getSaveFileName(
            self, caption="Select DB file",
            directory=path,
            options=QFileDialog.Option.DontConfirmOverwrite
        )
        if ok_:
            self.add_db_name(str(Path(db_name)))

    def verify_db_file(self, db_path: str) -> bool:
        """
        return  True if file is correct DB to store 'files data'
                    or empty/new file to create new DB
                False otherwise
        """
        path = Path(db_path).resolve(strict=False)
        if path.exists():
            if path.is_file():
                if path.stat().st_size == 0:                 # empty file
                    create_db.create_tables(db_path)
                    return True
                msg = create_db.check_app_schema(db_path)
                if msg == "Ok":
                    return True
                self.msg = f'{msg}: "{db_path}"'
                return False
        else:                           # new DB file
            create_db.create_tables(db_path)
            return True

    @pyqtSlot(QTableWidgetItem)
    def item_click(self, item: QTableWidgetItem):
        it = self.listDB.item(item.row(), 0)
        db_path, used, _ = it.data(Qt.ItemDataRole.UserRole)
        self.check_and_open(db_path, used)

    def open_db(self, db_path: str):
        if ag.db.conn:
            tug.save_app_setting(
                FILE_LIST_HEADER=ag.file_list.header().saveState()
            )
        self.save_db_list(ag.db.path, db_path, self.get_item_list())
        logger.info(f'open_db_signal.emit {db_path}')
        ag.signals.open_db_signal.emit(db_path)
        self.close()

    def check_and_open(self, db_path: str, used: bool=False) -> bool:
        if used:
            return False
        path = Path(db_path).resolve(strict=False)
        if not path.exists():
            msg = "not exist DB file"
        else:
            msg = create_db.check_app_schema(db_path)
            if msg == "Ok":
                self.open_db(db_path)
                return True

        logger.info(f'{self.msg=}: "{db_path}"')
        show_message_box('Error open DB', f'{msg}: "{db_path}"',
            icon=QStyle.StandardPixmap.SP_MessageBoxCritical
        )
        return False

    def open_in_new_window(self, db_path: str):
        if ag.db.conn:
            tug.save_app_setting(FILE_LIST_HEADER=ag.file_list.header().saveState())
        ag.signals.user_signal.emit(f'MainMenu New window\\{db_path}')
        self.close()

    def get_item_list(self) -> list:
        rows = {}
        for i in range(self.listDB.rowCount()):
            path, used, dt = self.listDB.item(i, 0).data(Qt.ItemDataRole.UserRole)
            rows[path] = (used, dt)
        return sorted([(k,*v) for k,v in rows.items()], key=lambda x: x[2], reverse=True)

    def mark_not_used(self, row: int):
        def msg_callback(res: int):
            if res == 1:
                item.setData(Qt.ItemDataRole.UserRole, (path, False, dt))
                self.listDB.setItem(row, 1, QTableWidgetItem(f'{dt!s}'))
                self.save_db_list(path)

        item = self.listDB.item(row, 0)
        path, _, dt = item.data(Qt.ItemDataRole.UserRole)
        name = Path(path).name
        show_message_box(
            f'DB "{name}" marked as in use',
            'Do you want to mark it as not in use?',
            btn=QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel,
            icon=QStyle.StandardPixmap.SP_MessageBoxQuestion,
            details=f'Be sure that DB "{name}" is not in use by other instance of {ag.app_name()}',
            callback=msg_callback
        )

    def save_db_list(self, db_close:str='', db_open: str='', dblist: list=[]):
        now = str(datetime.now().replace(microsecond=0))
        db_list = dblist if dblist else tug.get_app_setting("DB_List", [])
        for i,item in enumerate(db_list):
            if item[0] == db_close:
                db_list[i] = (item[0], False, now)
            elif item[0] == db_open:
                db_list[i] = (item[0], True, now)

        tug.save_app_setting(DB_List=db_list)

    def closeEvent(self, a0):
        ag.popups.pop("OpenDB")
        return super().closeEvent(a0)
