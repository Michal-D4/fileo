from pathlib import Path
from loguru import logger

from PyQt6.QtCore import Qt, pyqtSlot, QPoint
from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtWidgets import (QFileDialog, QLabel,
    QListWidgetItem, QVBoxLayout, QWidget, QMenu,
    QApplication,
)

from ..core import create_db, icons, utils, app_globals as ag
from .ui_open_db import Ui_openDB


class listItem(QWidget):

    def __init__(self, name: str, path: str, parent = None) -> None:
        super().__init__(parent)

        self.row = QVBoxLayout()

        self.name = QLabel(name)
        self.path = QLabel(path)

        self.row.addWidget(self.name)
        self.row.addWidget(self.path)

        self.set_style()
        self.setLayout(self.row)

    def get_db_name(self) -> str:
        return '/'.join((self.path.text(), self.name.text()))

    def set_style(self):
        self.name.setStyleSheet(ag.dyn_qss['name'][0])
        self.path.setStyleSheet(ag.dyn_qss['path'][0])


class OpenDB(QWidget, Ui_openDB):

    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)

        self.setupUi(self)
        self.msg = ''

        self.restore_db_list()

        self.open_btn.setIcon(icons.get_other_icon("open_db"))
        self.open_btn.clicked.connect(self.add_db)

        self.listDB.doubleClicked.connect(self.item_click)
        self.listDB.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.listDB.customContextMenuRequested.connect(self.item_menu)
        self.listDB.currentItemChanged.connect(self.row_changed)
        self.listDB.setCurrentRow(0)

        self.input_path.textEdited.connect(self.style_input_path)
        self.input_path.editingFinished.connect(self.finish_edit)
        self.input_path.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.input_path.customContextMenuRequested.connect(self.path_menu)

        escape = QShortcut(QKeySequence(Qt.Key.Key_Escape), self)
        escape.activated.connect(self.close)
        self.set_tool_tip()

    @pyqtSlot(QListWidgetItem, QListWidgetItem)
    def row_changed(self, curr: QListWidgetItem, prev: QListWidgetItem):
        wid: listItem = self.listDB.itemWidget(curr)
        self.input_path.setText(wid.get_db_name())
        self.set_tool_tip()

    @pyqtSlot(QPoint)
    def item_menu(self, pos: QPoint):
        item = self.listDB.itemAt(pos)
        if item:
            db_name = self.input_path.text()
            menu = self.db_list_menu(
                db_name[db_name.rfind('/')+1:]
            )
            action = menu.exec(self.listDB.mapToGlobal(pos))
            if action:
                menu_item_text = action.text()
                if menu_item_text.endswith('window'):
                    self.open_in_new_window(db_name)
                    return
                if menu_item_text.startswith('Delete'):
                    self.remove_item(item)
                    return
                if menu_item_text.startswith('Open'):
                    self.open_db(db_name)

    def db_list_menu(self, db_name: str) -> QMenu:
        menu = QMenu(self)
        menu.addAction(f'Open DB "{db_name}"')
        menu.addSeparator()
        menu.addAction(f'Open DB "{db_name}" in new window')
        menu.addSeparator()
        menu.addAction(f'Delete DB "{db_name}" from list')
        return menu

    def set_tool_tip(self):
        self.input_path.setToolTip(
            'Enter path to create database or choose from '
            'the list below. Esc - to close without choice'
        )
        self.input_path.setPlaceholderText(
            "Enter path to open/create database. "
            "Esc - to close without choice"
        )

    @pyqtSlot(QPoint)
    def path_menu(self, pos: QPoint):
        menu = QMenu(self)
        menu.addAction("Copy message")
        action = menu.exec(self.input_path.mapToGlobal(pos))
        if action:
            self.copy_message()

    def copy_message(self):
        if self.input_path.text():
            QApplication.clipboard().setText(self.input_path.text())
        else:
            QApplication.clipboard().setText(self.input_path.placeholderText())

    def restore_db_list(self):
        db_list = utils.get_app_setting("DB_List", []) or []
        for it in db_list:
            self.add_item_widget(it)

    def add_item_widget(self, full_name: str):
        item = QListWidgetItem(type=QListWidgetItem.ItemType.UserType)
        self.listDB.addItem(item)

        path = Path(full_name)
        item_widget = listItem(path.name, path.parent.as_posix())
        item.setSizeHint(item_widget.sizeHint())

        self.listDB.setItemWidget(item, item_widget)

    def remove_item(self, item: 'QListWidgetItem'):
        self.listDB.takeItem(self.listDB.row(item))

    def style_input_path(self, text: str):
        self.input_path.setStyleSheet(ag.dyn_qss['input_path_edited'][0])
        self.input_path.setToolTip('Esc - to close without choice')

    def finish_edit(self):
        if self.msg:
            return
        db_name = self.input_path.text()
        if db_name:
            self.add_db_name(Path(db_name).as_posix())

    def show_error_message(self):
        if not self.msg:
            return
        self.input_path.setStyleSheet(ag.dyn_qss['input_path_message'][0])

        self.input_path.clear()
        self.input_path.setPlaceholderText(self.msg)
        self.input_path.setToolTip(self.msg)
        self.msg = ''

    def add_db_name(self, db_name:str):
        db_ = db_name.strip()
        logger.info(db_)
        if self.open_if_here(db_):
            return

        self.open_if_ok(db_)

    def open_if_ok(self, db_name: str):
        if self.verify_db_file(db_name):
            logger.info(f"{self.msg=}")
            self.add_item_widget(db_name)
            self.open_db(db_name)
            return
        self.show_error_message()

    def open_if_here(self, db_name: str) -> bool:
        for item in self.get_item_list():
            if item == db_name:
                self.open_db(db_name)
                return True
        return False

    def add_db(self):
        pp = Path('~/fileo/dbs').expanduser()
        path = utils.get_app_setting('DEFAULT_DB_PATH', pp.as_posix())
        db_name, ok_ = QFileDialog.getSaveFileName(
            self, caption="Select DB file",
            directory=path,
            options=QFileDialog.Option.DontConfirmOverwrite
        )
        if ok_:
            self.add_db_name(Path(db_name).as_posix())

    def verify_db_file(self, file_name: str) -> bool:
        """
        return  True if file is correct DB to store 'files data'
                    or empty/new file to create new DB
                False otherwise
        """
        file_ = Path(file_name).resolve(strict=False)
        logger.info(self.input_path.text())
        logger.info(self.input_path.placeholderText())
        self.input_path.setText(file_name)
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
    def item_click(self):
        self.open_db(self.input_path.text())

    def open_db(self, db_name: str):
        ag.signals_.get_db_name.emit(db_name)
        self.close()

    def open_in_new_window(self, db_name: str):
        ag.signals_.user_signal.emit(f'Setup New window/{db_name}')
        self.close()

    def get_item_list(self) -> list:
        items = []
        for i in range(self.listDB.count()):
            item = self.listDB.item(i)
            wit: listItem = self.listDB.itemWidget(item)
            items.append(wit.get_db_name())
        items.sort(key=str.lower, reverse=True)
        return items

    def close(self) -> bool:
        self.msg = 'closing'
        logger.info(f"{self.msg=}")
        utils.save_app_setting(DB_List=self.get_item_list())
        return super().close()
