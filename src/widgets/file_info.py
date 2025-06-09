# from loguru import logger

from PyQt6.QtCore import Qt, QDateTime
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtWidgets import (QWidget, QFormLayout, QLabel,
    QLineEdit, QVBoxLayout, QScrollArea, QFrame, QApplication,
    QMenu,
)

from ..core import app_globals as ag, db_ut


class fileInfo(QWidget):
    def __init__(self, parent = None) -> None:
        super().__init__(parent)

        self.file_id = 0

        self.rating = QLineEdit()
        self.rating.setObjectName('edit_rating')
        self.pages = QLineEdit()
        self.pages.setObjectName('edit_pages')
        self.rating.editingFinished.connect(self.rating_changed)
        self.pages.editingFinished.connect(self.pages_changed)

        self.form_setup()
        self.set_event_handler()

    def copy_file_data(self, e: QMouseEvent, row: int):
        def copy_row(i: int) -> str:
            fld = self.form_layout.itemAt(i, QFormLayout.ItemRole.FieldRole).widget()
            lbl = self.form_layout.itemAt(i, QFormLayout.ItemRole.LabelRole).widget()
            return f'{lbl.text()}\t{fld.text()}'

        if e.buttons() is Qt.MouseButton.RightButton:
            menu = QMenu(self)
            menu.addAction('Copy current line')
            menu.addAction('Copy all')
            act = menu.exec(e.globalPosition().toPoint())
            if act:
                if act.text() == 'Copy current line':
                    QApplication.clipboard().setText(copy_row(row))
                elif act.text() == 'Copy all':
                    tt = [f'{copy_row(0)};  file_id: {self.file_id}']
                    for i in range(1, self.form_layout.rowCount()):
                        tt.append(copy_row(i))
                    QApplication.clipboard().setText('\n'.join(tt))

    def set_event_handler(self):
        for i in range(self.form_layout.rowCount()):
            fld = self.form_layout.itemAt(i, QFormLayout.ItemRole.FieldRole).widget()
            if isinstance(fld, QLabel):
                fld.mousePressEvent = lambda event, row=i: self.copy_file_data(event, row)

    def rating_changed(self):
        db_ut.update_files_field(self.file_id, 'rating', self.rating.text())

    def pages_changed(self):
        db_ut.update_files_field(self.file_id, 'pages', self.pages.text())

    def set_file_id(self, id: int):
        self.file_id = id
        self.populate_fields()

    def form_setup(self):
        self.form_layout = QFormLayout()
        self.form_layout.setContentsMargins(9, 9, 9, 9)

        self.form_layout.addRow("File name:", QLabel())
        self.form_layout.addRow("Path:", QLabel())
        self.form_layout.addRow("Added date:", QLabel())
        self.form_layout.addRow("Last opened date:", QLabel())
        self.form_layout.addRow("Modified date:", QLabel())
        self.form_layout.addRow("Created date:", QLabel())
        self.form_layout.addRow("Publication date(book):", QLabel())
        self.form_layout.addRow("File opened (times):", QLabel())
        self.form_layout.addRow("File rating:", self.rating)
        self.form_layout.addRow("Size of file:", QLabel())
        self.form_layout.addRow("Pages(book):", self.pages)


        self.form_info = QFrame(self)
        self.form_info.setObjectName('form_info')
        self.form_info.setLayout(self.form_layout)

        scroll = QScrollArea()
        scroll.setObjectName("scrollFileInfo")
        scroll.setWidget(self.form_info)
        scroll.setWidgetResizable(True)

        v_layout = QVBoxLayout(self)
        v_layout.setContentsMargins(0, 0, 0, 0)
        v_layout.addWidget(scroll)

    def populate_fields(self):
        idx = ag.file_list.currentIndex()
        if idx.isValid():
            self.file_id = idx.data(Qt.ItemDataRole.UserRole)
            fields = db_ut.get_file_info(self.file_id)
            if not fields:
                return
            for i in range(self.form_layout.rowCount()):
                if i >= 2 and i <= 6:
                    field = self.time_value(fields[i])
                elif i == 9:
                    field = ag.human_readable_size(fields[i])
                else:
                    field = fields[i]
                self.form_layout.itemAt(
                    i, QFormLayout.ItemRole.FieldRole
                    ).widget().setText(str(field))

    def time_value(self, val: int) -> str:
        a = QDateTime()
        a.setSecsSinceEpoch(val)
        return a.toString("dd/MM/yyyy hh:mm")
