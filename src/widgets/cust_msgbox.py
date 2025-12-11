# from loguru import logger
from PyQt6.QtCore import Qt, QPoint, QSize
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtWidgets import (QStyle, QMessageBox,
    QPushButton, QDialog, QLayout,
)

from .ui_cust_msgbox import Ui_msgBox
from .. import tug
from ..core import app_globals as ag


class CustomMessageBox(QDialog, Ui_msgBox):
    toggle_btn_text = ["Show Details...", "Hide Details..."]

    def __init__(self, msg: str, parent=None):
        super().__init__(parent)
        self.start_pos = QPoint()
        self.setupUi(self)
        self.setWindowFlags(
            Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint
        )
        self.msg.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.details.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.msg.setText(msg)
        self.details.setWordWrap(True)
        self.details_show = False
        self.toggle_btn = QPushButton(self)
        self.toggle_btn.setText(self.toggle_btn_text[self.details_show])
        self.toggle_btn.setVisible(self.details_show)
        self.horizontalLayout.addWidget(self.toggle_btn)
        self.det_frame.setVisible(self.details_show)
        self.ico.setPixmap(tug.get_icon('ico_app').pixmap(24, 24))
        self.mouseMoveEvent = self.move_self
        self.box_layout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)
        self.layout().setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)

    def set_title(self, ttl: str):
        self.title.setText(ttl)

    def set_buttons(self, buttons: QMessageBox.StandardButton=QMessageBox.StandardButton.Close):
        available_btns = {   # and corresponding roles: "AcceptRole" and "RejectRole"
            "Apply": QMessageBox.ButtonRole.AcceptRole,
            "Ok": QMessageBox.ButtonRole.AcceptRole,
            "Open": QMessageBox.ButtonRole.AcceptRole,
            "Cancel": QMessageBox.ButtonRole.RejectRole,
            "Close": QMessageBox.ButtonRole.RejectRole,
        }
        for x in QMessageBox.StandardButton:
            if x & buttons:
                btn = QPushButton(self)
                btn.clicked.connect(self.accept if available_btns[x.name] is QMessageBox.ButtonRole.AcceptRole else self.reject)
                btn.setText(x.name)
                self.horizontalLayout.addWidget(btn)

    def move_self(self, e: QMouseEvent):
        if e.buttons() == Qt.MouseButton.LeftButton:
            pos_ = e.globalPosition().toPoint()
            dist = pos_ - self.start_pos
            if dist.manhattanLength() < 50:
                self.move(self.pos() + dist)
                e.accept()
            self.start_pos = pos_

    def set_details(self, details: str):
        if details:
            self.details.setText(details)
            mm = self.details.fontMetrics()
            txt_sz = mm.size(Qt.TextFlag.TextSingleLine, details)

            fr_width = self.width() - 40
            fr_height = txt_sz.height() * (txt_sz.width() // fr_width + 3)
            self.det_frame.setMinimumHeight(fr_height)

            self.toggle_btn.setVisible(True)
            self.toggle_btn.clicked.connect(self.toggle_show_details)

    def toggle_show_details(self):
        self.details_show = not self.details_show
        if self.details_show:
            self.resize(self.width(), self.height() + self.det_frame.minimumHeight())
            self.toggle_btn.setMinimumWidth(self.toggle_btn.width())
        else:
            self.resize(self.width(), self.height() - self.det_frame.minimumHeight())

        self.det_frame.setVisible(self.details_show)
        self.toggle_btn.setText(self.toggle_btn_text[self.details_show])

    def set_msg_icon(self, icon=QStyle.StandardPixmap.SP_MessageBoxInformation):
        ico = QStyle.standardIcon(self.style(), icon)
        self.msg_ico.setPixmap(ico.pixmap(QSize(32, 32)))


def show_message_box(
        title: str, msg: str,
        btn: QMessageBox.StandardButton = QMessageBox.StandardButton.Close,
        icon = QStyle.StandardPixmap.SP_MessageBoxInformation,
        details: str = '',
        callback=None):
    dlg = CustomMessageBox(msg, ag.app)
    if callback:
        dlg.finished.connect(callback)   # parameter: result: int
    dlg.set_title(title)
    dlg.set_buttons(btn)
    dlg.set_msg_icon(icon)
    dlg.set_details(details)
    dlg.open()
    return dlg
