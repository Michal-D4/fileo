# from loguru import logger
from pathlib import Path

from PyQt6.QtCore import Qt, QCoreApplication, QPoint, pyqtSlot, QSize
from PyQt6.QtGui import QMouseEvent, QKeySequence
from PyQt6.QtWidgets import (QWidget, QFormLayout,
    QLineEdit, QCheckBox, QComboBox, QHBoxLayout,
)

from .. import tug
from ..core import app_globals as ag
from .foldable import Foldable
from .ui_pref import Ui_prefForm

SIZE_RATIO = {
    '8pt': 0.90,
    '9pt': 0.95,
    '10pt': 1.00,
    '11pt': 1.05,
    '12pt': 1.10,
    '14pt': 1.15,
}

class Preferences(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_prefForm()
        self.ui.setupUi(self)
        self.cur_size = self.init_size = self.size()
        self.ui.ico.setPixmap(tug.get_icon('ico_app').pixmap(24, 24))

        self.start_pos = QPoint()
        self.cur_theme = ''
        self.cur_font_size = ''
        self.rejected = True

        self.set_inputs()

        form_layout = QFormLayout()

        form_layout.addRow('Color theme:', self.themes)
        form_layout.addRow('Font size:', self.fontsize)
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
        form_layout.addRow(self.save_theme)

        self.ui.pref_form.setLayout(form_layout)
        self.adjustSize()

        self.mouseMoveEvent = self.move_self
        self.ui.accept_pref.clicked.connect(self.accept)
        self.ui.accept_pref.setShortcut(QKeySequence(Qt.Key.Key_Return))
        self.ui.cancel.clicked.connect(self.close)
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

    def reject(self):
        theme_key = self.themes.currentData(Qt.ItemDataRole.UserRole)
        if self.cur_font_size != self.fontsize.currentText():
            tug.save_app_setting(FONT_SIZE=self.cur_font_size)
            self.set_theme(self.cur_theme)
            return
        if theme_key != self.cur_theme:
            self.set_theme(self.cur_theme)

    def accept(self):
        settings = {
            "Current Theme": (
                self.themes.currentText(),
                self.themes.currentData(Qt.ItemDataRole.UserRole)
            ),
            "DEFAULT_DB_PATH": self.db_path.text(),
            "DEFAULT_EXPORT_PATH": self.export_path.text(),
            "DEFAULT_REPORT_PATH": self.report_path.text(),
            "DEFAULT_FILE_PATH": self.file_path.text(),
            "DEFAULT_LOG_PATH": self.log_path.text(),
            "FOLDER_HISTORY_DEPTH": self.folder_history_depth.text(),
            "RECENT_FILE_LIST_LENGTH": self.last_file_list_length.text(),
            "CHECK_DUPLICATES": int(self.check_dup.isChecked()),
            "CHECK_UPDATE": int(self.check_upd.isChecked()),
            "USE_LOGGING": int(self.use_logging.isChecked()),
            "SAVE_THEME": int(self.save_theme.isChecked()),
        }
        tug.save_app_setting(**settings)
        tug.create_dir(Path(self.db_path.text()))
        tug.create_dir(Path(self.export_path.text()))
        tug.create_dir(Path(self.report_path.text()))
        tug.create_dir(Path(self.file_path.text()))
        tug.create_dir(Path(self.log_path.text()))
        ag.history.set_limit(int(settings["FOLDER_HISTORY_DEPTH"]))
        self.rejected = False
        self.close()

    def set_inputs(self):
        self.themes = QComboBox()
        for key, theme in tug.themes.items():
            self.themes.addItem(theme['name'], userData=key)
        _theme, self.cur_theme = tug.get_app_setting(
            "Current Theme", ("Default Theme", "Default_Theme")
        )
        self.themes.setCurrentText(_theme)
        self.themes.currentIndexChanged.connect(self.change_theme)

        self.fontsize = QComboBox()
        for key in tug.FONT_SIZE:
            self.fontsize.addItem(key)
        self.cur_font_size = tug.get_app_setting('FONT_SIZE', '10pt')
        self.fontsize.setCurrentText(self.cur_font_size)
        self.cur_size = self.init_size * SIZE_RATIO[self.cur_font_size]
        self.fontsize.currentIndexChanged.connect(self.change_font_size)

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

        self.save_theme = QCheckBox("save color theme")
        self.save_theme.setChecked(int(tug.get_app_setting('SAVE_THEME', 0)))

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

    def change_font_size(self, idx: int):
        f_size = self.fontsize.currentText()
        tug.save_app_setting(FONT_SIZE=f_size)
        self.set_theme(self.themes.currentData(Qt.ItemDataRole.UserRole))
        self.cur_size = self.init_size * SIZE_RATIO[f_size]
        self.adjustSize()
        ag.app.adjustSize()
        ag.signals_.font_size_changed.emit(f_size)

    def change_theme(self, idx: int):
        self.set_theme(self.themes.currentData(Qt.ItemDataRole.UserRole))

    def set_theme(self, theme_key):
        styles = tug.prepare_styles(theme_key, to_save=self.save_theme.isChecked())
        QCoreApplication.instance().setStyleSheet(styles)
        self.apply_dyn_qss()
        self.set_icons()
        self.save_theme.setChecked(False)

    def apply_dyn_qss(self):
        Foldable.set_decorator_qss(tug.get_dyn_qss('decorator', -1))
        for fs in ag.fold_grips:
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

        def set_checked_tool_btn():
            checkable_btn = {
                ag.appMode.DIR: ag.app.ui.btnDir,
                ag.appMode.FILTER: ag.app.ui.btnFilter,
                ag.appMode.FILTER_SETUP: ag.app.ui.btnFilterSetup,
            }
            mode = (ag.mode if ag.mode in
                    (ag.appMode.DIR, ag.appMode.FILTER, ag.appMode.FILTER_SETUP)
                    else ag.appMode(ag.curr_btn_id))
            btn = checkable_btn.get(mode, ag.app.ui.btnDir)
            btn.setIcon(tug.get_icon(btn.objectName(), 1))
            btn.setChecked(True)

        set_icons_from_list(ag.buttons)
        set_icons_from_list(ag.note_buttons)

        pix = tug.get_icon("busy", 0)
        ag.app.ui.busy.setPixmap(pix.pixmap(16, 16))
        set_checked_tool_btn()

    @pyqtSlot()
    def close(self) -> bool:
        ag.popups.pop("Preferences")
        if self.rejected:
            self.reject()
        return super().close()