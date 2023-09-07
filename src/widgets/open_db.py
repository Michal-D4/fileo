from pathlib import Path
from loguru import logger

from PyQt6.QtCore import Qt, pyqtSlot, QPoint
from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtWidgets import (QFileDialog, QHBoxLayout, QLabel,
    QListWidgetItem, QToolButton, QVBoxLayout, QWidget, QMenu,
    QApplication,
)

from ..core import create_db, icons, utils, app_globals as ag
from .ui_open_db import Ui_openDB


class listItem(QWidget):

    def __init__(self, name: str, path: str, parent = None) -> None:
        super().__init__(parent)

        self.row = QHBoxLayout()
        self.name_path = QVBoxLayout()

        self.name = QLabel(name)
        self.path = QLabel(path)

        self.remove_btn = QToolButton()
        self.remove_btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.remove_btn.setAutoRaise(True)

        self.remove_btn.setIcon(icons.get_other_icon("remove_btn"))

        self.name_path.addWidget(self.name)
        self.name_path.addWidget(self.path)

        self.row.addLayout(self.name_path, 1)
        self.row.addWidget(self.remove_btn, 0)

        self.set_style()
        self.setLayout(self.row)

    def set_style(self):
        self.name.setStyleSheet(ag.dyn_qss['name'][0])
        self.path.setStyleSheet(ag.dyn_qss['path'][0])


class OpenDB(QWidget):

    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)

        self.ui = Ui_openDB()
        self.ui.setupUi(self)
        self.db_list = None
        self.msg = ''

        self.restore_db_list()

        self.ui.open_btn.setIcon(icons.get_other_icon("open_db"))

        self.ui.listDB.itemClicked.connect(self.item_click)
        self.ui.open_btn.clicked.connect(self.add_db)

        self.ui.input_path.textEdited.connect(self.qss_input_path_edited)
        self.ui.input_path.editingFinished.connect(self.finish_edit)
        self.ui.input_path.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.ui.input_path.customContextMenuRequested.connect(self.path_menu)

        ag.signals_.close_db_dialog.connect(self.lost_focus)
        escape = QShortcut(QKeySequence(Qt.Key.Key_Escape), self)
        escape.activated.connect(self.lost_focus)
        self.set_tool_tip()

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
        self.db_list = utils.get_app_setting("DB_List", []) or []
        for it in self.db_list:
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

            row.remove_btn.clicked.connect(
                lambda state, rr=item: self.remove_item(wit=rr)
            )

    @pyqtSlot('QListWidgetItem')
    def remove_item(self, wit: 'QListWidgetItem'):
        row = self.ui.listDB.row(wit)
        self.ui.listDB.takeItem(row)
        self.db_list.remove(wit.data(Qt.ItemDataRole.UserRole))

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
        if db_name not in self.db_list:
            self.add_item_widget(db_name)
            self.db_list.append(db_name)

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
        ag.signals_.get_db_name.emit(
            self.ui.listDB.currentItem().data(Qt.ItemDataRole.UserRole))
        self.close()

    def close(self) -> bool:
        utils.save_app_setting(**{"DB_List": self.db_list})
        return super().close()
