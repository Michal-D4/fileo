from loguru import logger
from pathlib import Path

from PyQt6 import QtCore
from PyQt6.QtWidgets import (QDialog, QFormLayout, QFrame,
    QLineEdit, QSpinBox, QHBoxLayout,  QVBoxLayout,
    QDialogButtonBox, QSizePolicy, QSpacerItem,
    QCheckBox,
)

from ..core import utils, app_globals as ag

def create_dir(dir: Path):
    dir.mkdir(parents=True, exist_ok=True)

class Preferencies(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle('Application preferencies')
        self.buttonBox = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        form_layout = QFormLayout()
        form_layout.setContentsMargins(9, 9, 9, 9)
        self.set_inputs()

        form_layout.addRow('Path to DBs:', self.db_path)
        form_layout.addRow('Export path:', self.export_path)
        form_layout.addRow('Report path:', self.report_path)
        form_layout.addRow('Log file path:', self.log_path)
        form_layout.addRow('Folder history depth:', self.folder_history_depth)
        form_layout.addRow('Allow single instance only:', self.single_instance)
        form_layout.addRow('Switch on logging:', self.do_log)
        form_layout.addRow('Logging to stderr:', self.stderr_log)
        form_layout.addRow('Write QSS to log file:', self.qss_log)

        v_layout = QVBoxLayout(self)
        v_layout.setContentsMargins(9, 9, 9, 9)
        v_layout.setSpacing(16)

        form = QFrame(self)
        form.setLayout(form_layout)

        spacer_item = QSpacerItem(20, 286, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        h_layout = QHBoxLayout()
        h_layout.addSpacerItem(spacer_item)
        h_layout.addWidget(self.buttonBox)
        v_layout.addWidget(form)
        v_layout.addLayout(h_layout)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self.setModal(True)

    def sizeHint(self) -> QtCore.QSize:
        return QtCore.QSize(499,184)

    def accept(self):
        settings = {
            "DEFAULT_DB_PATH": self.db_path.text(),
            "DEFAULT_EXPORT_PATH": self.export_path.text(),
            "DEFAULT_REPORT_PATH": self.report_path.text(),
            "DEFAULT_LOG_PATH": self.log_path.text(),
            "FOLDER_HISTORY_DEPTH": self.folder_history_depth.value(),
            "SINGLE_INSTANCE": int(self.single_instance.isChecked()),
            "SWITCH_ON_LOGGING": int(self.do_log.isChecked()),
            "LOGGING_TO_STDERR": int(self.stderr_log.isChecked()),
            "LOG_QSS": int(self.qss_log.isChecked()),
        }
        utils.save_app_setting(**settings)
        create_dir(Path(self.db_path.text()))
        create_dir(Path(self.export_path.text()))
        create_dir(Path(self.report_path.text()))
        create_dir(Path(self.log_path.text()))
        ag.history.set_limit(int(settings["FOLDER_HISTORY_DEPTH"]))
        ag.single_instance = bool(settings["SINGLE_INSTANCE"])
        self.close()

    def set_inputs(self):
        self.db_path = QLineEdit()
        pp = Path('~/fileo').expanduser()
        self.db_path.setText(
            utils.get_app_setting('DEFAULT_DB_PATH', str(pp / 'dbs'))
        )
        self.export_path = QLineEdit()
        self.export_path.setText(
            utils.get_app_setting('DEFAULT_EXPORT_PATH', str(pp / 'export'))
        )
        self.report_path = QLineEdit()
        self.report_path.setText(
            utils.get_app_setting('DEFAULT_REPORT_PATH', str(pp / 'report'))
        )
        self.log_path = QLineEdit()
        self.log_path.setText(
            utils.get_app_setting('DEFAULT_LOG_PATH', str(pp / 'log'))
        )
        self.folder_history_depth = QSpinBox()
        self.folder_history_depth.setMinimum(2)
        self.folder_history_depth.setMaximum(50)
        val = utils.get_app_setting('FOLDER_HISTORY_DEPTH', 15)
        self.folder_history_depth.setValue(int(val))
        ag.history.set_limit(int(val))
        self.single_instance = QCheckBox()
        self.single_instance.setChecked(
            int(utils.get_app_setting('SINGLE_INSTANCE', 0))
        )
        self.do_log = QCheckBox()
        self.do_log.setChecked(
            int(utils.get_app_setting('SWITCH_ON_LOGGING', 0))
        )
        self.stderr_log = QCheckBox()
        self.stderr_log.setChecked(
            int(utils.get_app_setting('LOGGING_TO_STDERR', 0))
        )
        self.qss_log = QCheckBox()
        self.qss_log.setChecked(
            int(utils.get_app_setting('LOG_QSS', 0))
        )
