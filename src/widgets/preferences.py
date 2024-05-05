from loguru import logger
from pathlib import Path

from PyQt6.QtCore import QSize, Qt, QCoreApplication, QPoint
from PyQt6.QtGui import QMouseEvent, QPixmap
from PyQt6.QtWidgets import (QWidget, QFormLayout, QFrame,
    QLineEdit, QSpinBox, QHBoxLayout,  QVBoxLayout,
    QDialogButtonBox, QSizePolicy, QSpacerItem,
    QCheckBox, QComboBox,
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
        self.ui.ico.setPixmap(QPixmap(tug.qss_params['$ico_app']))

        self.start_pos = QPoint()
        self.cur_theme = ''

        form_layout = QFormLayout()
        form_layout.setContentsMargins(9, 9, 9, 9)
        self.set_inputs()

        form_layout.addRow('Color theme:', self.themes)
        form_layout.addRow('Path to DBs:', self.db_path)
        form_layout.addRow('Export path:', self.export_path)
        form_layout.addRow('Report path:', self.report_path)
        form_layout.addRow('Log file path:', self.log_path)
        form_layout.addRow('Folder history depth:', self.folder_history_depth)
        form_layout.addRow('Check duplicates:', self.check_dup)
        if tug.config['instance_control']:
            form_layout.addRow('Allow single instance only:', self.single_instance)

        self.ui.pref_form.setLayout(form_layout)

        self.mouseMoveEvent = self.move_self
        self.ui.accept_pref.clicked.connect(self.accept)
        self.ui.cancel.clicked.connect(self.reject)

    def move_self(self, e: QMouseEvent):
        if e.buttons() == Qt.MouseButton.LeftButton:
            pos_ = e.globalPosition().toPoint()
            dist = pos_ - self.start_pos
            if dist.manhattanLength() < 50:
                self.move(self.pos() + dist)
                e.accept()
            self.start_pos = pos_

    def sizeHint(self) -> QSize:
        return QSize(499,184)

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
            "DEFAULT_LOG_PATH": self.log_path.text(),
            "FOLDER_HISTORY_DEPTH": self.folder_history_depth.value(),
            "CHECK_DUPLICATES": int(self.check_dup.isChecked()),
        }
        if tug.config['instance_control']:
            settings['SINGLE_INSTANCE'] = int(self.single_instance.isChecked())
            ag.single_instance = bool(settings["SINGLE_INSTANCE"])
        tug.save_app_setting(**settings)
        tug.create_dir(Path(self.db_path.text()))
        tug.create_dir(Path(self.export_path.text()))
        tug.create_dir(Path(self.report_path.text()))
        tug.create_dir(Path(self.log_path.text()))
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
        self.log_path = QLineEdit()
        self.log_path.setText(
            tug.get_app_setting('DEFAULT_LOG_PATH', str(pp / 'log'))
        )
        self.folder_history_depth = QSpinBox()
        self.folder_history_depth.setMinimum(2)
        self.folder_history_depth.setMaximum(50)
        val = tug.get_app_setting('FOLDER_HISTORY_DEPTH', 15)
        self.folder_history_depth.setValue(int(val))
        ag.history.set_limit(int(val))
        self.check_dup = QCheckBox()
        self.check_dup.setChecked(
            int(tug.get_app_setting('CHECK_DUPLICATES', 1))
        )
        if tug.config['instance_control']:
            self.single_instance = QCheckBox()
            self.single_instance.setChecked(
                int(tug.get_app_setting('SINGLE_INSTANCE', 0))
            )

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

    def set_icons(self):
        def set_icons_from_list(buttons):
            for btn, *icons in buttons:
                if len(icons) > 1:
                    btn.setIcon(tug.get_icon(icons[btn.isChecked()]))
                else:
                    btn.setIcon(tug.get_icon(icons[0], btn.isChecked()))

        set_icons_from_list(ag.buttons)
        set_icons_from_list(ag.note_buttons)

        pix = tug.get_icon("busy", 0)
        ag.app.ui.busy.setPixmap(pix.pixmap(16, 16))
