from loguru import logger

from PyQt6.QtCore import Qt, QDateTime, QSize
from PyQt6.QtWidgets import (QWidget, QFormLayout, QLabel,
    QLineEdit, QVBoxLayout, QScrollArea, QFrame, QSizePolicy,
    QGroupBox,
)

from core import app_globals as ag, db_ut, icons


class fileInfo(QWidget):
    def __init__(self, parent = None) -> None:
        super().__init__(parent)

        self.id = 0

        self.rating = QLineEdit()
        self.pages = QLineEdit()
        self.rating.editingFinished.connect(self.rating_changed)
        self.pages.editingFinished.connect(self.pages_changed)

        self.form_setup()
        self.setObjectName('fileInfo')
        # size_policy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        # size_policy.setHorizontalStretch(0)
        # size_policy.setVerticalStretch(0)
        # self.setSizePolicy(size_policy)
        # self.setMinimumSize(QSize(0, 0))
        # self.setMaximumSize(QSize(16777215, 16777215))

        logger.info(ag.dyn_qss["fileInfo"][0])
        self.setStyleSheet(ag.dyn_qss["fileInfo"][0])

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


        form = QFrame(self)
        form.setLayout(self.form_layout)

        scroll = QScrollArea()
        scroll.setWidget(form)
        scroll.setWidgetResizable(True)

        v_layout = QVBoxLayout(self)
        v_layout.setContentsMargins(0, 0, 0, 0)
        v_layout.addWidget(scroll)
        # v_layout.addWidget(form)
        # self.setLayout(v_layout)

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
            for i in range(self.form_layout.rowCount()):
            # for i,field in enumerate(fields):
                if i >= 2 and i <= 5:
                    field = self.time_value(fields[i])
                else:
                    field = fields[i]
                self.form_layout.itemAt(
                    i, QFormLayout.ItemRole.FieldRole
                    ).widget().setText(str(field))

    def time_value(self, val: int) -> str:
        a = QDateTime()
        a.setSecsSinceEpoch(val)
        return a.toString("dd/MM/yyyy hh:mm")
