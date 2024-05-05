from pathlib import Path
from loguru import logger
from datetime import datetime

from PyQt6.QtCore import Qt, pyqtSlot, QPoint
from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtWidgets import (QFileDialog, QLabel,
    QListWidgetItem, QHBoxLayout, QWidget, QMenu,
    QMessageBox,
)

from ..core import create_db, app_globals as ag
from .ui_open_db import Ui_openDB
from .. import tug

TIME_0 = datetime(1, 1, 1)

class listItem(QWidget):

    def __init__(self, item_data: tuple, parent = None) -> None:
        super().__init__(parent)

        self.row = QHBoxLayout()

        self.last_use: datetime = item_data[2]
        self.path = item_data[1]
        self.name = QLabel(item_data[0])
        self.use_date = QLabel(f'{self.last_use!s}')

        self.row.addWidget(self.name)
        self.row.addStretch(0)
        self.row.addWidget(self.use_date)

        self.set_style()
        self.setLayout(self.row)

    def get_item_data(self) -> tuple:
        return '/'.join((self.path, self.name.text())), self.last_use

    def set_style(self):
        self.name.setStyleSheet(tug.get_dyn_qss('the-name'))
        self.use_date.setStyleSheet(tug.get_dyn_qss('use-date'))


class OpenDB(QWidget, Ui_openDB):

    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)

        self.setupUi(self)
        self.msg = ''

        self.restore_db_list()

        self.listDB.itemDoubleClicked.connect(self.item_click)
        self.listDB.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.listDB.customContextMenuRequested.connect(self.item_menu)
        self.listDB.setCurrentRow(0)

        enter = QShortcut(QKeySequence(Qt.Key.Key_Return), self)
        enter.activated.connect(self.item_enter)

        escape = QShortcut(QKeySequence(Qt.Key.Key_Escape), self)
        escape.activated.connect(self.close)

    @pyqtSlot(QPoint)
    def item_menu(self, pos: QPoint):
        item: QListWidgetItem = self.listDB.itemAt(pos)
        if item:
            db_name, _ = self.listDB.itemWidget(item).get_item_data()
            menu = self.db_list_menu(
                db_name[db_name.rfind('/')+1:]
            )
            action = menu.exec(self.listDB.mapToGlobal(pos))
            if action:
                menu_item_text = action.text()
                if menu_item_text.endswith('window'):
                    self.open_in_new_window(db_name)
                elif menu_item_text.startswith('Delete'):
                    self.remove_item(item)
                elif menu_item_text.startswith('Open'):
                    self.open_db(db_name)
                elif menu_item_text.startswith('Reveal'):
                    tug.reveal_file(db_name)

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
        db_list = tug.get_app_setting("DB_List", []) or []
        for it in db_list:
            # the last is the first in the list !!!
            self.add_item_widget((it, TIME_0) if isinstance(it, str) else it)

    def add_item_widget(self, item_data: tuple):
        item = QListWidgetItem(type=QListWidgetItem.ItemType.UserType)
        self.listDB.addItem(item)

        path = Path(item_data[0])
        item_widget = listItem(
            (path.name, str(path.parent), item_data[1])
        )
        item.setSizeHint(item_widget.sizeHint())

        self.listDB.setItemWidget(item, item_widget)

    def remove_item(self, item: 'QListWidgetItem'):
        self.listDB.takeItem(self.listDB.row(item))

    def add_db_name(self, db_name:str):
        db_ = db_name.strip()
        if self.open_if_here(db_):
            return

        self.open_if_ok(db_)

    def open_if_ok(self, db_name: str):
        if self.verify_db_file(db_name):
            self.add_item_widget(db_name)
            self.open_db(db_name)
            return
        ag.show_message_box(
            'Error open DB',
            self.msg,
            icon=QMessageBox.Icon.Critical
        )

    def open_if_here(self, db_name: str) -> bool:
        for item in self.get_item_list():
            if item == db_name:
                self.open_db(db_name)
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
    def item_enter(self):
        self.item_click(self.listDB.currentItem())

    @pyqtSlot(QListWidgetItem)
    def item_click(self, item: QListWidgetItem):
        item_data = self.listDB.itemWidget(item).get_item_data()
        self.open_db(item_data[0])

    def open_db(self, db_name: str):
        ag.signals_.get_db_name.emit(db_name)
        self.close()

    def open_in_new_window(self, db_name: str):
        ag.signals_.user_signal.emit(f'MainMenu New window\\{db_name}')
        self.close()

    def get_item_list(self) -> list:
        items = []
        cur_db = ag.db.path
        for i in range(self.listDB.count()):
            item = self.listDB.item(i)
            wit: listItem = self.listDB.itemWidget(item)
            data = wit.get_item_data()
            if data[0] == cur_db:
                dt = datetime.now()
                data = (data[0], dt.replace(microsecond=0))
            items.append(data)
        return sorted(items, key=lambda x: x[1], reverse=False)

    def close(self) -> bool:
        tug.save_app_setting(DB_List=self.get_item_list())
        tug.open_db = None
        return super().close()
