from loguru import logger

from PyQt6.QtCore import Qt, QDateTime
from PyQt6.QtWidgets import (QWidget, QFormLayout, QLabel,
    QLineEdit, QVBoxLayout, QFrame,
)

from core import app_globals as ag, db_ut, icons


class fileInfo(QWidget):
    def __init__(self, parent = None) -> None:
        super().__init__(parent)

        self.id = 0

        self.form_setup()
        self.setObjectName('fileInfo')
        logger.info(ag.dyn_qss["fileInfo"][0])
        self.setStyleSheet(ag.dyn_qss["fileInfo"][0])

        self.rating.editingFinished.connect(self.rating_changed)
        self.pages.editingFinished.connect(self.pages_changed)

    def rating_changed(self):
        logger.info(f"{self.rating.text()=}")
        db_ut.update_files_field(self.id, 'rating', self.rating.text())

    def pages_changed(self):
        logger.info(f"{self.pages.text()=}")
        db_ut.update_files_field(self.id, 'pages', self.pages.text())

    def set_file_id(self, id: int):
        self.id = id
        self.populate_fields()

    def form_setup(self):
        form = QFrame(self)
        self.rating = QLineEdit()
        self.pages = QLineEdit()

        self.form_layout = QFormLayout()
        self.form_layout.setContentsMargins(9, 9, 9, 9)
        self.form_layout.addRow("File name:", QLabel())
        self.form_layout.addRow("Path:", QLabel())
        self.form_layout.addRow("Last opened date:", QLabel())
        self.form_layout.addRow("Modified date:", QLabel())
        self.form_layout.addRow("Created date:", QLabel())
        self.form_layout.addRow("Publication date(book):", QLabel())
        self.form_layout.addRow("File opened (times):", QLabel())
        self.form_layout.addRow("File rating:", self.rating)
        self.form_layout.addRow("Size of file:", QLabel())
        self.form_layout.addRow("Pages(book):", self.pages)
        form.setLayout(self.form_layout)

        v_layout = QVBoxLayout()
        v_layout.setContentsMargins(0, 0, 0, 0)
        v_layout.addWidget(form)
        self.setLayout(v_layout)

    def populate_fields(self):
        """
        populate all fields
        except QComboBox from authors table
        """
        idx = ag.file_list.currentIndex()
        u_dat: ag.FileData = idx.data(Qt.ItemDataRole.UserRole)
        if u_dat:
            self.id = u_dat.id
            fields = db_ut.get_file_info(self.id)
            if not fields:
                return
            for i,field in enumerate(fields):
                if i >= 2 and i <= 5:
                    field = self.time_value(field)
                self.form_layout.itemAt(
                    i, QFormLayout.ItemRole.FieldRole
                    ).widget().setText(str(field))

    def time_value(self, val: int) -> str:
        a = QDateTime()
        a.setSecsSinceEpoch(val)
        return a.toString("dd/MM/yyyy hh:mm")
