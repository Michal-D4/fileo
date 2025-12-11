# from loguru import logger
from pathlib import Path

from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QMouseEvent, QKeySequence
from PyQt6.QtWidgets import (QWidget, QFormLayout,
    QLineEdit, QCheckBox, QHBoxLayout,
)

from .. import tug
from ..core import app_globals as ag
from .ui_pref import Ui_prefForm


class Preferences(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_prefForm()
        self.ui.setupUi(self)
        self.cur_size = self.init_size = self.size()
        self.ui.ico.setPixmap(tug.get_icon('ico_app').pixmap(24, 24))

        self.start_pos = QPoint()

        self.set_inputs()

        form_layout = QFormLayout()

        form_layout.addRow('Path to DBs:', self.db_path)
        form_layout.addRow('Export path:', self.export_path)
        form_layout.addRow('Report path:', self.report_path)
        form_layout.addRow('Files path:', self.file_path)
        form_layout.addRow('Log path:', self.log_path)

        h_lay0 = QHBoxLayout()
        h_lay0.addWidget(self.folder_history_depth, 1)
        h_lay0.addStretch(5)
        form_layout.addRow('Folder history depth:', h_lay0)

        h_lay1 = QHBoxLayout()
        h_lay1.addWidget(self.last_file_list_length, 1)
        h_lay1.addStretch(5)
        form_layout.addRow('Recent file list length:', h_lay1)

        form_layout.addRow(self.check_upd)
        form_layout.addRow(self.check_dup)
        form_layout.addRow(self.use_logging)

        self.ui.pref_form.setLayout(form_layout)
        self.adjustSize()

        self.mouseMoveEvent = self.move_self
        self.ui.accept_pref.clicked.connect(self.accept)
        self.ui.accept_pref.setShortcut(QKeySequence(Qt.Key.Key_Return))
        self.ui.cancel.clicked.connect(self.close)
        ag.signals.font_size_changed.connect(self.font_changed)
        ag.popups["Preferences"] = self

    def sizeHint(self):
        return self.cur_size

    def move_self(self, e: QMouseEvent):
        if e.buttons() == Qt.MouseButton.LeftButton:
            pos_ = e.globalPosition().toPoint()
            dist = pos_ - self.start_pos
            if dist.manhattanLength() < 50:
                self.move(self.pos() + dist)
                e.accept()
            self.start_pos = pos_

    def accept(self):
        settings = {
            "DEFAULT_DB_PATH": self.db_path.text(),
            "DEFAULT_EXPORT_PATH": self.export_path.text(),
            "DEFAULT_REPORT_PATH": self.report_path.text(),
            "DEFAULT_FILE_PATH": Path(self.file_path.text()).as_posix(),
            "DEFAULT_LOG_PATH": self.log_path.text(),
            "FOLDER_HISTORY_DEPTH": self.folder_history_depth.text(),
            "RECENT_FILE_LIST_LENGTH": self.last_file_list_length.text(),
            "CHECK_DUPLICATES": int(self.check_dup.isChecked()),
            "CHECK_UPDATE": int(self.check_upd.isChecked()),
            "USE_LOGGING": int(self.use_logging.isChecked()),
        }
        tug.save_app_setting(**settings)
        tug.create_dir(Path(self.db_path.text()))
        tug.create_dir(Path(self.export_path.text()))
        tug.create_dir(Path(self.report_path.text()))
        tug.create_dir(Path(self.file_path.text()))
        tug.create_dir(Path(self.log_path.text()))
        ag.history.set_limit(int(settings["FOLDER_HISTORY_DEPTH"]))
        self.close()

    def set_inputs(self):
        pp = Path('~/fileo').expanduser()
        self.db_path = QLineEdit()
        self.db_path.setText(
            tug.get_app_setting('DEFAULT_DB_PATH', str(pp / 'dbs'))
        )
        self.export_path = QLineEdit()
        self.export_path.setText(
            tug.get_app_setting('DEFAULT_EXPORT_PATH', str(pp / 'export'))
        )
        self.report_path = QLineEdit()
        self.report_path.setText(
            tug.get_app_setting('DEFAULT_REPORT_PATH', str(pp / 'report'))
        )
        self.file_path = QLineEdit()
        self.file_path.setText(
            tug.get_app_setting('DEFAULT_FILE_PATH', str(pp / 'files'))
        )

        self.log_path = QLineEdit()
        self.log_path.setText(
            tug.get_app_setting('DEFAULT_LOG_PATH', str(pp / 'log'))
        )

        self.folder_history_depth = QLineEdit()
        self.folder_history_depth.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.folder_history_depth.editingFinished.connect(self.history_depth_changed)
        val = tug.get_app_setting('FOLDER_HISTORY_DEPTH', 15)
        self.folder_history_depth.setText(str(val))

        self.last_file_list_length = QLineEdit()
        self.last_file_list_length.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.last_file_list_length.editingFinished.connect(self.file_list_length_changed)
        val = tug.get_app_setting('RECENT_FILE_LIST_LENGTH', 30)
        self.last_file_list_length.setText(str(val))
        ag.recent_files_length = int(val)

        self.check_dup = QCheckBox("check duplicates")
        self.check_dup.setChecked(
            int(tug.get_app_setting('CHECK_DUPLICATES', 1))
        )

        self.check_upd = QCheckBox("check for updates")
        self.check_upd.setChecked(
            int(tug.get_app_setting('CHECK_UPDATE', 0))
        )

        self.use_logging = QCheckBox("use logging")
        self.use_logging.setChecked(int(tug.get_app_setting('USE_LOGGING', 0)))

    def history_depth_changed(self):
        val = int(self.folder_history_depth.text())
        n_val, x_val = 2, tug.qss_params.get('history_max', 50)
        if n_val > val:
            self.folder_history_depth.setText(str(n_val))
        elif x_val < val:
            self.folder_history_depth.setText(str(x_val))

    def file_list_length_changed(self):
        val = int(self.last_file_list_length.text())
        n_val, x_val = 2, 2 * tug.qss_params.get('history_max', 50)
        if n_val > val:
            self.last_file_list_length.setText(str(n_val))
        elif x_val < val:
            self.last_file_list_length.setText(str(x_val))

    def font_changed(self, idx: int):
        f_size = tug.get_app_setting("FONT_SIZE", "10")
        self.cur_size = self.init_size * tug.SIZE_RATIO[f_size]
        self.adjustSize()
        ag.app.adjustSize()
        ag.signals.font_size_changed.emit(f_size)

    def closeEvent(self, a0):
        ag.popups.pop("Preferences")
        return super().closeEvent(a0)
