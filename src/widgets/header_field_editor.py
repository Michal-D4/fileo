# from loguru import logger

from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import QWidget, QMessageBox, QStyle, QDialog

from .ui_field_editor import Ui_fldEditor
from .. import tug
from ..core import app_globals as ag


class fieldEditor(QWidget, Ui_fldEditor):
    """ idx - header section logical index """
    def __init__(self, idx: int, parent = None):
        super().__init__(parent)

        self.setupUi(self)
        self.index = idx
        self.typ = tug.qss_params['$FieldTypes'][self.index]
        self.set_data()

        self.ok.clicked.connect(self.save_new)
        self.cancel.clicked.connect(self.close)
        ag.popups["fieldEditor"] = self

    def set_data(self):
        def type_changed():
            ag.show_message_box(
                'Field type will be changed',
                f'Data in field "{self.title.text()}" will be lost. Please confirm',
                btn=QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel,
                icon=QStyle.StandardPixmap.SP_MessageBoxWarning,
                callback=handle_type_change
            )

        def handle_type_change(result: int):
            if result == QDialog.DialogCode.Accepted.value:
                if self.fld_type.currentText() == 'date' and not fmt:
                    self.fld_format.setText('yyyy-MM-dd hh:mm')
                self.tool_tip.setFocus()
            else:
                if self.fld_type.currentText() == 'date':
                    self.fld_format.setText(fmt)
                    self.fld_type.setCurrentText(self.typ)

        def title_edit_finished():
            nonlocal title
            title = self.title.text()
            self.fld_type.setFocus()

        def tool_tip_edit_finished():
            self.fld_format.setFocus()

        def format_edit_finished():
            nonlocal fmt
            fmt = self.fld_format.text()
            self.ok.setFocus()

        title = tug.qss_params['$FileListFields'][self.index]
        self.title.setText(title)
        fmt = tug.qss_params['$FieldFormats'][self.index]
        self.fld_type.setCurrentText(self.typ)
        self.tool_tip.setText(tug.qss_params['$ToolTips'][self.index])
        self.fld_format.setText('yyyy-MM-dd hh:mm' if not fmt and self.typ == 'date' else fmt)
        self.fld_type.currentIndexChanged.connect(type_changed)
        self.title.editingFinished.connect(title_edit_finished)
        self.tool_tip.editingFinished.connect(tool_tip_edit_finished)
        self.fld_format.editingFinished.connect(format_edit_finished)

    def save_new(self):
        def clear_field_in_db():
            if self.index not in (3,6,8):
                return
            fields = tug.qss_params['$EditableFields']
            vals = {'str': '', 'int': 0, 'date': ag.DATE_1970_1_1.toSecsSinceEpoch()}
            sql = f'update files set {fields[self.index]} = ?'
            with ag.db.conn as conn:
                conn.cursor().execute(sql, (vals[self.fld_type.currentText()],))

        title = self.title.text()
        fld_type = self.fld_type.currentText()
        if fld_type != self.typ:
            clear_field_in_db()
        tool_tip = self.tool_tip.text()
        fld_format = self.fld_format.text()
        ag.signals.user_signal.emit(
            f'header_field_changed\\{"ё".join((str(self.index),title,fld_type,self.typ,tool_tip,fld_format))}'
        )
        self.close()

    @pyqtSlot()
    def close(self) -> bool:
        ag.popups.pop("fieldEditor")
        return super().close()
