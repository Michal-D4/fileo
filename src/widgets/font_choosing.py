# from loguru import logger

from PyQt6.QtCore import Qt, QCoreApplication, QPoint, pyqtSlot
from PyQt6.QtGui import QMouseEvent, QFontDatabase
from PyQt6.QtWidgets import QWidget

from .ui_font_list import Ui_fontChooser
from ..core import app_globals as ag
from .. import tug
from .file_data import Page

class fontChooser(QWidget, Ui_fontChooser):
    def __init__(self, parent = None):
        super().__init__(parent)

        self.setupUi(self)
        self.start_pos = QPoint()
        self.rejected = True
        self.start_pos = QPoint()

        self.ico.setPixmap(tug.get_icon('ico_app').pixmap(24, 24))
        self.cur_font_size = tug.get_app_setting("FONT_SIZE", "10")
        self.font_family = tug.get_app_setting("FONT_FAMILY", tug.qss_params["$fontFamily"])

        self.set_sizes()
        self.set_fonts()

        self.ok.clicked.connect(self.accept)
        self.cancel.clicked.connect(self.close)
        self.sizes.currentIndexChanged.connect(self.font_changed)
        self.fonts.currentIndexChanged.connect(self.font_changed)
        ag.popups["fontChooser"] = self

    def mouseMoveEvent(self, e: QMouseEvent):
        if e.buttons() & Qt.MouseButton.LeftButton:
            pos_ = e.globalPosition().toPoint()
            dist = pos_ - self.start_pos
            if dist.manhattanLength() < 50:
                self.move(self.pos() + dist)
                e.accept()
            self.start_pos = pos_

    @pyqtSlot()
    def font_changed(self):
        tug.save_app_setting(FONT_SIZE=self.sizes.currentText())
        tug.save_app_setting(FONT_FAMILY=self.fonts.currentText())
        self.apply_theme()

    def apply_theme(self):
        theme_key = tug.get_app_setting("CurrentTheme", "Default_Theme")
        styles = tug.prepare_styles(theme_key, False)
        QCoreApplication.instance().setStyleSheet(styles)
        self.apply_dyn_qss()

    def apply_dyn_qss(self):
        ag.filter_dlg.set_selectors_style()
        ag.filter_dlg.set_pages_style()
        if ag.file_data.cur_page is Page.TAGS:
            ag.file_data.tagEdit.setStyleSheet(tug.get_dyn_qss("line_edit"))
        else:
            ag.file_data.tagEdit.setStyleSheet(tug.get_dyn_qss("line_edit_ro"))

        ag.file_data.passive_style()
        ag.file_data.cur_page_restyle()
        ag.file_data.file_info.setStyleSheet(tug.get_dyn_qss("line_edit,date_time_edit"))
        ag.signals.color_theme_changed.emit()

    @pyqtSlot()
    def accept(self):
        self.rejected = False
        self.apply_theme()
        self.close()

    def set_sizes(self):
        for sz in tug.FONT_SIZE:
            self.sizes.addItem(sz)
        self.sizes.setCurrentText(self.cur_font_size)

    def set_fonts(self):
        sty = tug.qss_params["$fontStyle"]
        for fam in QFontDatabase.families(QFontDatabase.WritingSystem.Latin):
            if sty in QFontDatabase.styles(fam):
                if '[' in fam: continue  # noqa: E701
                self.fonts.addItem(fam)
        self.fonts.setCurrentText(self.font_family)

    def reject(self):
        if self.cur_font_size != self.sizes.currentText() or self.font_family != self.fonts.currentText():
            tug.save_app_setting(FONT_SIZE=self.cur_font_size)
            tug.save_app_setting(FONT_FAMILY=self.font_family)
            self.apply_theme()

    def closeEvent(self, a0):
        ag.popups.pop("fontChooser")
        if self.rejected:
            self.reject()
        return super().closeEvent(a0)
