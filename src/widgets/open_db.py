from pathlib import Path
from loguru import logger

from PyQt6.QtCore import Qt, pyqtSlot, QPoint, QModelIndex
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

    def get_name(self) -> str:
        return self.name.text()

    def get_full_name(self) -> str:
        return '/'.join((self.path.text(), self.name.text()))

    def set_style(self):
        self.name.setStyleSheet(ag.dyn_qss['name'][0])
        self.path.setStyleSheet(ag.dyn_qss['path'][0])


class OpenDB(QWidget):

    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)

        self.ui = Ui_openDB()
        self.ui.setupUi(self)
        self.msg = ''

        self.restore_db_list()

        self.ui.open_btn.setIcon(icons.get_other_icon("open_db"))
        self.ui.open_btn.clicked.connect(self.add_db)

        self.ui.listDB.itemClicked.connect(self.item_click)
        self.ui.listDB.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.ui.listDB.customContextMenuRequested.connect(self.item_menu)
        self.ui.listDB.currentItemChanged.connect(self.row_changed)

        self.ui.input_path.textEdited.connect(self.qss_input_path_edited)
        self.ui.input_path.editingFinished.connect(self.finish_edit)
        self.ui.input_path.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.ui.input_path.customContextMenuRequested.connect(self.path_menu)

        ag.signals_.close_db_dialog.connect(self.lost_focus)
        escape = QShortcut(QKeySequence(Qt.Key.Key_Escape), self)
        escape.activated.connect(self.lost_focus)
        self.set_tool_tip()

    @pyqtSlot(QListWidgetItem, QListWidgetItem)
    def row_changed(self, curr: QListWidgetItem, prev: QListWidgetItem):
        wid: listItem = self.ui.listDB.itemWidget(curr)
        self.ui.input_path.setText(wid.get_full_name())

    @pyqtSlot(QPoint)
    def item_menu(self, pos: QPoint):
        item = self.ui.listDB.itemAt(pos)
        if item:
            wid: listItem = self.ui.listDB.itemWidget(item)
            db_name = wid.get_name()
            menu = self.db_list_menu(db_name)
            action = menu.exec(self.ui.listDB.mapToGlobal(pos))
            if action:
                menu_item_text = action.text()
                if menu_item_text.endswith('window'):
                    self.open_in_new_window(wid.get_full_name())
                    return
                if menu_item_text.startswith('Delete'):
                    self.remove_item(item)
                    return
                if menu_item_text.startswith('Open'):
                    self.open_db(wid.get_full_name())

    def db_list_menu(self, db_name: str) -> QMenu:
        menu = QMenu(self)
        menu.addAction(f'Open DB "{db_name}"')
        menu.addSeparator()
        menu.addAction(f'Open DB "{db_name}" in new window')
        menu.addSeparator()
        menu.addAction(f'Delete DB "{db_name}" from list')
        return menu

    def set_tool_tip(self):
        self.ui.input_path.setToolTip(
            'Enter path to create database or choose from '
            'the list below. Esc - to close without choice'
        )

    @pyqtSlot(QPoint)
    def path_menu(self, pos: QPoint):
        menu = QMenu(self)
        menu.addAction("Copy message")
        action = menu.exec(self.ui.input_path.mapToGlobal(pos))
        if action:
            self.copy_message()

    def copy_message(self):
        if self.ui.input_path.text():
            QApplication.clipboard().setText(self.ui.input_path.text())
        else:
            QApplication.clipboard().setText(self.ui.input_path.placeholderText())

    def restore_db_list(self):
        db_list = utils.get_app_setting("DB_List", []) or []
        for it in db_list:
            self.add_item_widget(it)
        self.ui.listDB.setCurrentRow(0)

    def add_item_widget(self, full_name: str):
        path = Path(full_name)
        if path.exists() and path.is_file():
            item = QListWidgetItem(self.ui.listDB)
            item.setData(Qt.ItemDataRole.UserRole, full_name)
            self.ui.listDB.addItem(item)

            row = listItem(str(path.name), str(path.parent))
            item.setSizeHint(row.sizeHint())

            self.ui.listDB.setItemWidget(item, row)

    @pyqtSlot('QListWidgetItem')
    def remove_item(self, wit: 'QListWidgetItem'):
        row = self.ui.listDB.row(wit)
        self.ui.listDB.takeItem(row)
        # self.db_list.remove(wit.data(Qt.ItemDataRole.UserRole))

    def qss_input_path_edited(self, text: str):
        self.ui.input_path.setStyleSheet(ag.dyn_qss['input_path_edited'][0])
        self.ui.input_path.setToolTip('Esc - to close without choice')

    def finish_edit(self):
        db_name = self.ui.input_path.text()
        if db_name:
            self.register_db_name(db_name)

    def register_db_name(self, db_name: str):
        if self.verify_db_file(db_name):
            self.add_db_name()
        else:
            self.show_error_message()

    def show_error_message(self):
        self.ui.input_path.setStyleSheet(ag.dyn_qss['input_path_message'][0])

        self.ui.input_path.clear()
        self.ui.input_path.setPlaceholderText(self.msg)
        self.ui.input_path.setToolTip(self.msg)

    def add_db_name(self):
        db_name = self.ui.input_path.text()
        if not self.is_here_already(db_name):
            self.add_item_widget(db_name)

    def is_here_already(self, db_name: str) -> bool:
        for item in self.get_item_list():
            if item == db_name:
                return True
        return False

    def add_db(self):
        pp = Path('~/fileo/dbs').expanduser()
        path = utils.get_app_setting('DEFAULT_DB_PATH', pp.as_posix())
        file_name, ok_ = QFileDialog.getSaveFileName(self,
            caption="Select DB file",
            directory=path,
            options=QFileDialog.Option.DontConfirmOverwrite)
        if ok_:
            self.register_db_name(file_name)

    def verify_db_file(self, file_name: str) -> bool:
        """
        return  True if file is correct DB to store 'files data'
                    or empty/new file to create new DB
                False otherwise
        """
        file_ = Path(file_name).resolve(False)
        self.ui.input_path.setText(str(file_))
        if file_.exists():
            if file_.is_file():
                if create_db.check_app_schema(str(file_)):
                    return True
                if file_.stat().st_size == 0:               # empty file
                    create_db.create_tables(
                        create_db.create_db(str(file_))
                    )
                    return True
                else:
                    self.msg = f"not DB: {file_}"
                    return False
        elif file_.parent.exists and file_.parent.is_dir():   # file not exist
            create_db.create_tables(
                create_db.create_db(str(file_))
            )
            return True
        else:
            self.msg = f"bad path: {file_}"
            return False

    @pyqtSlot()
    def lost_focus(self):
        self.close()

    @pyqtSlot()
    def item_click(self):
        item = self.ui.listDB.currentItem()
        wid: listItem = self.ui.listDB.itemWidget(item)
        logger.info(f'{wid.get_full_name()=}')

        self.open_db(wid.get_full_name())

    def open_db(self, db_name: str):
        ag.signals_.get_db_name.emit(db_name)
        self.close()

    def open_in_new_window(self, db_name: str):
        ag.signals_.user_signal.emit(f'Setup New window/{db_name}')
        self.close()

    def get_item_list(self) -> list:
        items = []
        self.ui.listDB
        for i in range(self.ui.listDB.count()):
            item = self.ui.listDB.item(i)
            wit: listItem = self.ui.listDB.itemWidget(item)
            items.append(wit.get_full_name())
        return items

    def close(self) -> bool:
        utils.save_app_setting(**{"DB_List": self.get_item_list()})
        return super().close()
