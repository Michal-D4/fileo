from loguru import logger

from PyQt6.QtCore import Qt, QPoint, QSize, QDateTime, pyqtSignal
from PyQt6.QtGui import QMouseEvent, QKeySequence, QShortcut, QTextCursor
from PyQt6.QtWidgets import (QWidget, QFrame, QFormLayout, QLabel,
    QLineEdit, QHBoxLayout, QVBoxLayout, QComboBox, QCompleter,
    QToolButton, QSizePolicy, QSpacerItem, QPlainTextEdit, QMenu,
    QApplication,
)

from core import app_globals as ag, db_ut, icons


class fileInfo(QWidget):
    # file_info_close = pyqtSignal()

    def __init__(self, parent = None) -> None:
        super().__init__(parent)

        self.id = 0        # file id

        self.form_layout = QFormLayout()
        self.form = QFrame(self)
        self.file_authors = QPlainTextEdit()
        self.rating = QLineEdit()
        self.pages = QLineEdit()
        self.combo = QComboBox()

        self.form_setup()
        self.populate_fields()

        self.setStyleSheet(ag.dyn_qss["dialog"][0])

        self.rating.editingFinished.connect(self.rating_changed)
        self.pages.editingFinished.connect(self.pages_changed)

    def rating_changed(self):
        logger.info(f"{self.rating.text()=}")
        db_ut.update_files_field(self.id, 'rating', self.rating.text())

    def pages_changed(self):
        logger.info(f"{self.pages.text()=}")
        db_ut.update_files_field(self.id, 'pages', self.pages.text())

    def form_setup(self):
        h_layout = QHBoxLayout()
        lbl = QLabel()
        lbl.setText("File info")
        lbl.setObjectName("hdr_lbl")
        h_layout.addWidget(lbl)

        h_layout.setContentsMargins(9, 6, 9, 6)
        h_layout.addSpacerItem(
            QSpacerItem(80, 10,
                QSizePolicy.Policy.Expanding,
                QSizePolicy.Policy.Minimum)
        )
        close_btn = QToolButton()
        close_btn.setAutoRaise(True)
        close_btn.setIcon(icons.get_other_icon("remove_btn")[0])
        # close_btn.clicked.connect(self.to_close)
        close_btn.setToolTip("Close (Esc)")
        h_layout.addWidget(close_btn)

        hdr = QFrame(self)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        hdr.setSizePolicy(sizePolicy)
        hdr.setObjectName("hrdFrame")
        hdr.setLayout(h_layout)
        hdr.setStyleSheet(ag.dyn_qss["dialog_hdr"][0])

        self.form_layout.setContentsMargins(9, 0, 9, 9)
        self.form_layout.addRow(QLabel("File name:"), QLabel())
        self.form_layout.addRow(QLabel("Path:"), QLabel())
        self.form_layout.addRow(QLabel("Last opened date:"), QLabel())
        self.form_layout.addRow(QLabel("Modified date:"), QLabel())
        self.form_layout.addRow(QLabel("Created date:"), QLabel())
        self.form_layout.addRow(QLabel("Publication date(book):"), QLabel())
        self.form_layout.addRow(QLabel("File opened (times):"), QLabel())
        self.form_layout.addRow(QLabel("File rating:"), self.rating)
        self.form_layout.addRow(QLabel("Size of file:"), QLabel())
        self.form_layout.addRow(QLabel("Pages(book):"), self.pages)

        self.file_authors.setPlaceholderText(
            "The author(s) will appear here if entered or picked in the combobox below"
        )
        self.file_authors.setReadOnly(True)
        self.file_authors.setMaximumSize(QSize(16777215, 50))
        self.form_layout.addRow(QLabel("Author(s)(book):"), self.file_authors)
        self.combo.setEditable(True)
        self.combo.setInsertPolicy(QComboBox.InsertPolicy.InsertAlphabetically)
        self.form_layout.addRow(QLabel("Author selector:"), self.combo)

        v_layout0 =  QVBoxLayout()
        v_layout0.setContentsMargins(0, 0, 0, 0)
        v_layout0.addWidget(hdr)
        v_layout0.addLayout(self.form_layout)

        self.form.setObjectName("form")
        self.form.setLayout(v_layout0)

        v_layout = QVBoxLayout(self)
        v_layout.addWidget(self.form)

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
