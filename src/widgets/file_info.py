# from loguru import logger

from PyQt6.QtCore import Qt, QDateTime, pyqtSlot, QPoint
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtWidgets import (QWidget, QFormLayout, QLabel,
    QLineEdit, QVBoxLayout, QScrollArea, QFrame, QApplication,
    QMenu, QHBoxLayout, QDateTimeEdit, QLayout,
)

from ..core import app_globals as ag, db_ut
from .. import tug


class fileInfo(QWidget):
    # mapping file_info rows to file_list header fields
    row_mapping = ((0, 0), (1, -1), (2, 1), (3, 2), (4, 5), (5, 10), (6, 8), (7, 4), (8, 3), (9, 7), (10, 6),)
    def __init__(self, parent = None) -> None:
        super().__init__(parent)

        self.file_id = 0
        self.field_types = tug.qss_params['$FieldTypes']
        self.set_pub_widget()
        self.set_rating_widget()
        self.set_pages_widget()
        self.form_setup()
        self.rows_bottom = self.calc_rows_bottom()

        self.setStyleSheet(' '.join((tug.get_dyn_qss("line_edit"), tug.get_dyn_qss("date_time_edit"))))
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.copy_data)

    def set_pub_widget(self, val=None):
        if self.field_types[8] == 'date':
            self.pub_date = QDateTimeEdit()
            if val:
                self.pub_date.setDateTime(val)
            self.pub_date.dateTimeChanged.connect(self.date_field_changed)
        else:
            self.pub_date = QLineEdit()
            if val:
                self.pub_date.setText(val)
            self.pub_date.setReadOnly(True)
            self.pub_date.mousePressEvent = self.pub_date_toggle_ro
            self.pub_date.editingFinished.connect(self.field_edit_finished)
        self.pub_date.setObjectName("pub_date")
        self.pub_date.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)

    def set_rating_widget(self, val=None):
        if self.field_types[3] == 'date':
            self.rating = QDateTimeEdit()
            if val:
                self.rating.setDateTime(val)
            self.rating.dateTimeChanged.connect(self.date_field_changed)
        else:
            self.rating = QLineEdit()
            if val:
                self.rating.setText(val)
            self.rating.setReadOnly(True)
            self.rating.mousePressEvent = self.rating_toggle_ro
            self.rating.editingFinished.connect(self.field_edit_finished)
        self.rating.setObjectName("rating")
        self.rating.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)

    def set_pages_widget(self, val=None):
        if self.field_types[6] == 'date':
            self.pages = QDateTimeEdit()
            if val:
                self.pages.setDateTime(val)
            self.pages.dateTimeChanged.connect(self.date_field_changed)
        else:
            self.pages = QLineEdit()
            if val:
                self.pages.setText(val)
            self.pages.setReadOnly(True)
            self.pages.mousePressEvent = self.pages_toggle_ro
            self.pages.editingFinished.connect(self.field_edit_finished)
        self.pages.setObjectName("pages")
        self.pages.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)

    @pyqtSlot()
    def field_edit_finished(self):
        if self.file_id:
            sender: QLineEdit = self.sender()
            sender.setReadOnly(True)
            val = sender.text()
            self.update_model(val, {'pub_date': 8, 'rating': 3, 'pages': 6}[self.sender().objectName()])

    @pyqtSlot(QDateTime)
    def date_field_changed(self, val: QDateTime):
        if self.file_id:
            self.update_model(val, {'pub_date': 8, 'rating': 3, 'pages': 6}[self.sender().objectName()])

    def pub_date_toggle_ro(self, e: QMouseEvent):
        self.pub_date.setReadOnly(False)
        self.pub_date.selectAll()

    def rating_toggle_ro(self, e: QMouseEvent):
        self.rating.setReadOnly(False)
        self.rating.selectAll()

    def pages_toggle_ro(self, e: QMouseEvent):
        self.pages.setReadOnly(False)
        self.pages.selectAll()

    def copy_data(self, pos: QPoint):
        formats = tug.qss_params['$FieldFormats']
        def copy_row(i: int) -> str:
            if i == 6:
                fld = self.pub_date
            elif i == 8:
                fld = self.rating
            elif i == 10:
                fld = self.pages
            else:
                fld = self.form_layout.itemAt(i, QFormLayout.ItemRole.FieldRole).widget()
            lbl = self.form_layout.itemAt(i, QFormLayout.ItemRole.LabelRole).widget()
            j = self.row_mapping[i][1]
            return f'{lbl.text()}\t{fld.dateTime().toString(formats[j]) if isinstance(fld, QDateTimeEdit) else fld.text()}'

        y = pos.y()
        for row in range(self.form_layout.rowCount()):
            if y < self.rows_bottom[row]:
                break
        else:
            row = -1

        menu = QMenu(self)
        if row > -1:
            menu.addAction('Copy current line')
        menu.addAction('Copy all')
        act = menu.exec(ag.file_data.mapToGlobal(pos))
        if act:
            if act.text() == 'Copy current line':
                QApplication.clipboard().setText(copy_row(row))
            elif act.text() == 'Copy all':
                tt = [f'{copy_row(0)};  file_id: {self.file_id}']
                for i in range(1, self.form_layout.rowCount()):
                    tt.append(copy_row(i))
                QApplication.clipboard().setText('\n'.join(tt))

    def update_model(self, val, col):
        idx = ag.file_list.currentIndex()
        model = ag.file_list.model()
        model.setData(model.index(idx.row(), col), val, Qt.ItemDataRole.EditRole)

    def set_file_id(self, file_id: int):
        self.file_id = 0
        self.populate_fields(file_id)
        self.file_id = file_id

    def editable_field_changed(self, changes: str):
        def replace_row6():
            self.set_pub_widget(val)
            self.form_layout.insertRow(row, title, self.prepare_row_6(idx))

        def replace_row8():
            self.set_rating_widget(val)
            self.form_layout.insertRow(row, title, self.prepare_row_8(idx))

        def replace_row10():
            self.set_pages_widget(val)
            self.form_layout.insertRow(row, title, self.prepare_row_10(idx))

        def reset_editable_field():
            row_type = self.field_types[idx]
            if row_type != fld_type:
                self.field_types[idx] = fld_type
                self.form_layout.removeRow(row)
                {6: replace_row6,
                 8: replace_row8,
                 10: replace_row10,
                }[row]()
            elif title != tug.qss_params['$FileListFields'][idx]:
                self.form_layout.itemAt(row, QFormLayout.ItemRole.LabelRole).widget().setText(title)

        def find_row():
            for i,j in self.row_mapping:
                if j == idx:
                    return i
            return -1

        ii, title, fld_type, *_ = changes.split('ё')    # ё most impossible symbol in title & toolTip
        val = {'str': '', 'int': '0', 'date': ag.DATE_1970_1_1}[fld_type]
        idx = int(ii)
        row = find_row()
        reset_editable_field()

    def prepare_row_6(self, idx: int) -> QWidget|QLayout:
            if self.field_types[idx] == 'str':
                fld = self.pub_date
            else:
                fld = QHBoxLayout()
                fld.addWidget(self.pub_date, 1)
                fld.addStretch(3)
            return fld

    def prepare_row_8(self, idx: int) -> QWidget|QLayout:
            if self.field_types[idx] == 'str':
                fld = self.rating
            else:
                fld = QHBoxLayout()
                fld.addWidget(self.rating, 1)
                fld.addStretch(3)
            return fld

    def prepare_row_10(self, idx: int) -> QWidget|QLayout:
            if self.field_types[idx] == 'str':
                fld = self.pages
            else:
                fld = QHBoxLayout()
                fld.addWidget(self.pages, 1)
                fld.addStretch(3)
            return fld

    def form_setup(self):
        self.form_layout = QFormLayout()
        self.form_layout.setContentsMargins(9, 9, 9, 9)

        for i,j in self.row_mapping:
            txt = f"{'Path' if j == -1 else tug.qss_params['$FileListFields'][j]}:"
            if i == 6:
                self.form_layout.addRow(txt, self.prepare_row_6(j))
            elif i == 8:
                self.form_layout.addRow(txt, self.prepare_row_8(j))
            elif i == 10:
                self.form_layout.addRow(txt, self.prepare_row_10(j))
            else:
                self.form_layout.addRow(txt, QLabel())

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

    def calc_rows_bottom(self):
        rows = []
        for i in range(1, self.form_layout.rowCount()):
            fld = self.form_layout.itemAt(i, QFormLayout.ItemRole.LabelRole).widget()
            rows.append(fld.pos().y())
        rows.append(rows[-1]+fld.height()+9)
        return rows

    def populate_fields(self, file_id: int):
        formats = tug.qss_params['$FieldFormats']
        def time_value(val: int) -> QDateTime:
            a = QDateTime()
            a.setSecsSinceEpoch(val) if isinstance(val, int) else ag.DATE_1970_1_1
            return a

        fields = db_ut.get_file_info(file_id)
        if not fields:
            self.pub_date.setDateTime(ag.DATE_1970_1_1) if isinstance(self.pub_date, QDateTimeEdit) else self.pub_date.setText('')
            self.rating.setDateTime(ag.DATE_1970_1_1) if isinstance(self.rating, QDateTimeEdit) else self.rating.setText('')
            self.pages.setDateTime(ag.DATE_1970_1_1) if isinstance(self.pages, QDateTimeEdit) else self.pages.setText('')
            for i in range(self.form_layout.rowCount()):
                if i in (6,8,10):
                    continue
                self.form_layout.itemAt(
                    i, QFormLayout.ItemRole.FieldRole
                    ).widget().setText('')
            return

        for i,j in self.row_mapping: # i - file_info row, j - for field_types, formats
            field = (time_value(fields[i]).toString(formats[j])
                     if j > 0 and self.field_types[j] == 'date' else
                     str(fields[i]))

            if i == 2:
                field = '  /  '.join((field, ag.fileSource(db_ut.file_add_reason(file_id)).name))
            elif i == 6:        # published
                (self.pub_date.setDateTime(QDateTime.fromString(field, formats[j]))
                 if isinstance(self.pub_date, QDateTimeEdit) else
                 self.pub_date.setText(field))
                continue
            elif i == 8:        # rating
                (self.rating.setDateTime(QDateTime.fromString(field, formats[j]))
                 if isinstance(self.rating, QDateTimeEdit) else
                 self.rating.setText(field))
                continue
            elif i == 9:        # size
                field = ag.human_readable_size(int(field))
            elif i == 10:       # pages
                (self.pages.setDateTime(QDateTime.fromString(field, formats[j]))
                 if isinstance(self.pages, QDateTimeEdit) else
                 self.pages.setText(field))
                continue
            self.form_layout.itemAt(i, QFormLayout.ItemRole.FieldRole).widget().setText(field)
