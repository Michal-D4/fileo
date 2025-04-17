# from loguru import logger
from pathlib import Path

from PyQt6.QtCore import Qt, QCoreApplication, QPoint
from PyQt6.QtGui import QMouseEvent, QKeySequence
from PyQt6.QtWidgets import (QWidget, QFormLayout,
    QLineEdit, QCheckBox, QComboBox, QHBoxLayout,
    QLabel,
)

from .. import tug
from ..core import app_globals as ag
from .foldable import Foldable
from .ui_pref import Ui_prefForm

class Preferences(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_prefForm()
        self.ui.setupUi(self)
        self.ui.ico.setPixmap(tug.get_icon('ico_app').pixmap(24, 24))

        self.start_pos = QPoint()
        self.cur_theme = ''

        form_layout = QFormLayout()
        form_layout.setContentsMargins(9, 9, 9, 9)
        self.log_path = QLabel()
        self.set_inputs()

        form_layout.addRow('Color theme:', self.themes)
        form_layout.addRow('Path to DBs:', self.db_path)
        form_layout.addRow('Export path:', self.export_path)
        form_layout.addRow('Report path:', self.report_path)
        form_layout.addRow('Folder history depth:', self.folder_history_depth)
        form_layout.addRow('Recent file list length:', self.last_file_list_length)
        form_layout.addRow(self.check_dup)
        if tug.config.get("all_preferences", 0):
            form_layout.addRow(self.single_instance)
            h_lay = QHBoxLayout()
            h_lay.addWidget(self.use_logging)
            h_lay.addWidget(self.log_path)
            form_layout.addRow(h_lay)

        self.ui.pref_form.setLayout(form_layout)

        self.mouseMoveEvent = self.move_self
        self.ui.accept_pref.clicked.connect(self.accept)
        self.ui.accept_pref.setShortcut(QKeySequence(Qt.Key.Key_Return))
        self.ui.cancel.clicked.connect(self.reject)
        self.ui.cancel.setShortcut(QKeySequence(Qt.Key.Key_Escape))

    def move_self(self, e: QMouseEvent):
        if e.buttons() == Qt.MouseButton.LeftButton:
            pos_ = e.globalPosition().toPoint()
            dist = pos_ - self.start_pos
            if dist.manhattanLength() < 50:
                self.move(self.pos() + dist)
                e.accept()
            self.start_pos = pos_

    def reject(self):
        theme_key = self.themes.currentData(Qt.ItemDataRole.UserRole)
        if theme_key != self.cur_theme:
            self.set_theme(self.cur_theme)
        super().close()

    def accept(self):
        settings = {
            "Current Theme": (
                self.themes.currentText(),
                self.themes.currentData(Qt.ItemDataRole.UserRole)
            ),
            "DEFAULT_DB_PATH": self.db_path.text(),
            "DEFAULT_EXPORT_PATH": self.export_path.text(),
            "DEFAULT_REPORT_PATH": self.report_path.text(),
            "FOLDER_HISTORY_DEPTH": self.folder_history_depth.text(),
            "RECENT_FILE_LIST_LENGTH": self.last_file_list_length.text(),
            "CHECK_DUPLICATES": int(self.check_dup.isChecked()),
        }
        if tug.config.get("all_preferences", 0):
            settings["SINGLE_INSTANCE"] = int(self.single_instance.isChecked())
            settings["USE_LOGGING"] = int(self.use_logging.isChecked())
            ag.single_instance = bool(settings["SINGLE_INSTANCE"])
        tug.save_app_setting(**settings)
        tug.create_dir(Path(self.db_path.text()))
        tug.create_dir(Path(self.export_path.text()))
        tug.create_dir(Path(self.report_path.text()))
        ag.history.set_limit(int(settings["FOLDER_HISTORY_DEPTH"]))
        super().close()

    def set_inputs(self):
        self.themes = QComboBox()
        for key, theme in tug.themes.items():
            self.themes.addItem(theme['name'], userData=key)
        _theme, self.cur_theme = tug.get_app_setting(
            "Current Theme", ("Default Theme", "Default_Theme")
        )
        self.themes.setCurrentText(_theme)
        self.themes.currentIndexChanged.connect(self.change_theme)
        self.db_path = QLineEdit()
        pp = Path('~/fileo').expanduser()
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
        self.folder_history_depth = QLineEdit()
        self.folder_history_depth.editingFinished.connect(self.history_depth_changed)
        val = tug.get_app_setting('FOLDER_HISTORY_DEPTH', 15)
        self.folder_history_depth.setText(str(val))
        ag.history.set_limit(int(val))

        self.last_file_list_length = QLineEdit()
        self.last_file_list_length.editingFinished.connect(self.file_list_length_changed)
        val = tug.get_app_setting('RECENT_FILE_LIST_LENGTH', 30)
        self.last_file_list_length.setText(str(val))
        ag.recent_files_length = int(val)

        self.check_dup = QCheckBox("check duplicates")
        self.check_dup.setChecked(
            int(tug.get_app_setting('CHECK_DUPLICATES', 1))
        )

        if tug.config.get('all_preferences', 0):
            self.single_instance = QCheckBox("single instance")
            self.single_instance.setChecked(
                int(tug.get_app_setting('SINGLE_INSTANCE', 0))
            )

            self.use_logging = QCheckBox("use logging")
            self.use_logging.stateChanged.connect(
                lambda state: self.log_path.setText(
                    f'log path: {tug.get_log_path()}' if state else ''
                )
            )
            self.use_logging.setChecked(
                int(tug.get_app_setting('USE_LOGGING', 0))
            )

    def history_depth_changed(self):
        val = int(self.folder_history_depth.text())
        n_val, x_val = tug.config.get('history_min', 2), tug.config.get('history_max', 50)
        if n_val > val:
            self.folder_history_depth.setText(str(n_val))
        elif x_val < val:
            self.folder_history_depth.setText(str(x_val))

    def file_list_length_changed(self):
        val = int(self.last_file_list_length.text())
        n_val, x_val = tug.config.get('history_min', 2), 2 * tug.config.get('history_max', 50)
        if n_val > val:
            self.last_file_list_length.setText(str(n_val))
        elif x_val < val:
            self.last_file_list_length.setText(str(x_val))

    def change_theme(self, idx: int):
        theme_key = self.themes.currentData(Qt.ItemDataRole.UserRole)
        self.set_theme(theme_key)

    def set_theme(self, theme_key: str):
        log_qss = tug.config.get("save_prepared_qss", False)
        styles = tug.prepare_styles(theme_key, to_save=log_qss)
        QCoreApplication.instance().setStyleSheet(styles)
        self.apply_dyn_qss()
        self.set_icons()

    def apply_dyn_qss(self):
        Foldable.set_decorator_qss(tug.get_dyn_qss('decorator', -1))
        for fs in ag.fold_states:
            fs.wid.set_hovering(False)

        if ag.file_data.cur_page.value == 0:  # Page.TAGS
            ag.file_data.tagEdit.setStyleSheet(tug.get_dyn_qss("line_edit"))
        else:
            ag.file_data.tagEdit.setStyleSheet(tug.get_dyn_qss("line_edit_ro"))

        ag.file_data.passive_style()
        ag.file_data.cur_page_restyle()
        ag.signals_.color_theme_changed.emit()

    def set_icons(self):
        def set_icons_from_list(buttons):
            for btn, *icons in buttons:
                if len(icons) > 1:
                    btn.setIcon(tug.get_icon(icons[btn.isChecked()]))
                else:
                    btn.setIcon(tug.get_icon(icons[0]))

        set_icons_from_list(ag.buttons)
        set_icons_from_list(ag.note_buttons)

        pix = tug.get_icon("busy", 0)
        ag.app.ui.busy.setPixmap(pix.pixmap(16, 16))
