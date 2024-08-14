from pathlib import Path
from loguru import logger
from datetime import datetime

from PyQt6.QtCore import Qt, pyqtSlot, QPoint
from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtWidgets import (QFileDialog, QMenu,
    QTableWidgetItem, QWidget, QMessageBox,
    QHeaderView,
)

from ..core import create_db, app_globals as ag
from .ui_open_db import Ui_openDB
from .. import tug

TIME_0 = datetime(1, 1, 1)

class OpenDB(QWidget, Ui_openDB):

    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)

        self.setupUi(self)
        self.msg = ''
        self.curr_db = ''

        self.restore_db_list()
        self.listDB.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.listDB.itemEntered.connect(self.item_enter)
        self.listDB.itemDoubleClicked.connect(self.item_click)
        self.listDB.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.listDB.customContextMenuRequested.connect(self.item_menu)
        self.listDB.setCurrentCell(0, 0)

        return_key = QShortcut(QKeySequence(Qt.Key.Key_Return), self)
        return_key.activated.connect(self.keystroke)

        escape = QShortcut(QKeySequence(Qt.Key.Key_Escape), self)
        escape.activated.connect(self.close)

    @pyqtSlot(QTableWidgetItem)
    def item_enter(self, item: QTableWidgetItem):
        self.listDB.selectRow(item.row())

    @pyqtSlot(QPoint)
    def item_menu(self, pos: QPoint):
        item: QTableWidgetItem = self.listDB.itemAt(pos)
        if item:
            if item.column() > 0:
                item = self.listDB.item(item.row(), 0)
            db_name = str(item.data(Qt.ItemDataRole.DisplayRole))
            menu = self.db_list_menu(db_name)
            db_path = item.data(Qt.ItemDataRole.UserRole)
            action = menu.exec(self.listDB.mapToGlobal(pos))
            if action:
                menu_item_text = action.text()
                if menu_item_text.endswith('window'):
                    self.open_in_new_window(db_path)
                elif menu_item_text.startswith('Delete'):
                    self.remove_row(item.row())
                elif menu_item_text.startswith('Open'):
                    self.open_db(db_path)
                elif menu_item_text.startswith('Reveal'):
                    tug.reveal_file(db_path)

    def db_list_menu(self, db_name: str) -> QMenu:
        menu = QMenu(self)
        menu.addAction(f'Open DB "{db_name}"')
        menu.addSeparator()
        if not ag.single_instance:
            menu.addAction(f'Open DB "{db_name}" in new window')
            menu.addSeparator()
        menu.addAction(f'Reveal "{db_name}" in explorer')
        menu.addSeparator()
        menu.addAction(f'Delete DB "{db_name}" from list')
        return menu

    def restore_db_list(self):
        self.listDB.setHorizontalHeaderItem(0, QTableWidgetItem('DB name'))
        self.listDB.setHorizontalHeaderItem(1, QTableWidgetItem('last use date'))
        db_list = tug.get_app_setting("DB_List", [])

        row = 0
        for path, last_use in db_list:
            if not path:
                continue
            pp = Path(path)
            self.set_item0(path, row)
            self.listDB.setItem(row, 1, QTableWidgetItem(f'{last_use!s}'))
            row += 1

    def set_item0(self, db_path: str, row: int=0):
        self.listDB.insertRow(row)
        item0 = QTableWidgetItem()
        item0.setData(Qt.ItemDataRole.DisplayRole, Path(db_path).name)
        item0.setData(Qt.ItemDataRole.UserRole, db_path)
        self.listDB.setItem(row, 0, item0)

    def remove_row(self, row: int):
        self.listDB.removeRow(row)

    def add_db_name(self, db_path:str):
        logger.info(f'{db_path=}')
        if self.open_if_here(db_path):
            return

        self.open_if_ok(db_path)

    def open_if_ok(self, db_path: str):
        if self.verify_db_file(db_path):
            self.set_item0(db_path)
            self.open_db(db_path)
            return
        ag.show_message_box(
            'Error open DB',
            self.msg,
            icon=QMessageBox.Icon.Critical
        )

    def open_if_here(self, db_path: str) -> bool:
        for item in self.get_item_list():
            if item == db_path:
                self.open_db(db_path)
                return True
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

    def verify_db_file(self, file_name: str) -> bool:
        """
        return  True if file is correct DB to store 'files data'
                    or empty/new file to create new DB
                False otherwise
        """
        file_ = Path(file_name).resolve(strict=False)
        if file_.exists():
            if file_.is_file():
                if create_db.check_app_schema(file_name):
                    return True
                if file_.stat().st_size == 0:               # empty file
                    create_db.create_tables(
                        create_db.create_db(file_name)
                    )
                    return True
                else:
                    self.msg = f"not DB: {file_name}"
                    return False
        elif file_.parent.exists and file_.parent.is_dir():   # file not exist
            create_db.create_tables(
                create_db.create_db(file_name)
            )
            return True
        else:
            self.msg = f"bad path: {file_name}"
            return False

    @pyqtSlot()
    def keystroke(self):
        self.item_click(self.listDB.currentItem())

    @pyqtSlot(QTableWidgetItem)
    def item_click(self, item: QTableWidgetItem):
        it = self.listDB.item(item.row(), 0)
        db_path = str(it.data(Qt.ItemDataRole.UserRole))
        self.open_db(db_path)

    def open_db(self, db_path: str):
        self.curr_db = ag.db.path
        ag.signals_.get_db_name.emit(db_path)
        self.close()

    def open_in_new_window(self, db_path: str):
        ag.signals_.user_signal.emit(f'MainMenu New window\\{db_path}')
        self.close()

    def get_item_list(self) -> list:
        items = []
        for i in range(self.listDB.rowCount()):
            path = self.listDB.item(i, 0).data(Qt.ItemDataRole.UserRole)
            if path == self.curr_db:
                dt = datetime.now()
                last_use = str(dt.replace(microsecond=0))
            else:
                item1 = self.listDB.item(i, 1)
                dt = datetime.now()
                last_use = (
                    item1.data(Qt.ItemDataRole.DisplayRole) if
                    item1 else str(dt.replace(microsecond=0))
                )
            items.append((path, last_use))
        return sorted(items, key=lambda x: x[1], reverse=True)

    def close(self) -> bool:
        tug.save_app_setting(DB_List=self.get_item_list())
        tug.open_db = None
        db_list = tug.get_app_setting("DB_List", [])
        return super().close()
