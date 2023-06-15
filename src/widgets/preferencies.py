from loguru import logger
from pathlib import Path

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

        form_layout.addRow('Default path to DBs:', self.db_path)
        form_layout.addRow('Default export path:', self.export_path)
        form_layout.addRow('Folder history depth:', self.folder_history_depth)
        form_layout.addRow('Allow single instance only:', self.single_instance)

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
        self.setModal(True)

    def accept(self):
        settings = {
            "DEFAULT_DB_PATH": self.db_path.text(),
            "DEFAULT_EXPORT_PATH": self.export_path.text(),
            "FOLDER_HISTORY_DEPTH": self.folder_history_depth.value(),
            "SINGLE_INSTANCE": int(self.single_instance.isChecked())
        }
        utils.save_app_setting(**settings)
        create_dir(Path(self.db_path.text()))
        create_dir(Path(self.export_path.text()))
        ag.history.set_limit(settings["FOLDER_HISTORY_DEPTH"])
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
        self.folder_history_depth = QSpinBox()
        self.folder_history_depth.setMinimum(2)
        self.folder_history_depth.setMaximum(50)
        val = utils.get_app_setting('FOLDER_HISTORY_DEPTH', 15)
        self.folder_history_depth.setValue(val)
        ag.history.set_limit(val)
        self.single_instance = QCheckBox()
        self.single_instance.setChecked(
            utils.get_app_setting('SINGLE_INSTANCE', 0)
        )