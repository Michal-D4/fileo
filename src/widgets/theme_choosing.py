# from loguru import logger

from PyQt6.QtCore import Qt, QCoreApplication, QPoint, pyqtSlot
from PyQt6.QtGui import QMouseEvent, QKeySequence, QShortcut
from PyQt6.QtWidgets import QWidget, QListWidgetItem

from .ui_theme_list import Ui_themeList
from ..core import app_globals as ag
from .. import tug
from .file_data import Page

class themeChooser(QWidget, Ui_themeList):
    def __init__(self, parent = None):
        super().__init__(parent)

        self.setupUi(self)
        self.start_pos = QPoint()
        self.rejected = True

        self.cur_theme = tug.get_app_setting("CurrentTheme", "Default_Theme")
        self.cur_row = 0

        self.set_themes()

        self.theme_list.currentRowChanged.connect(self.apply_theme)
        self.theme_list.itemDoubleClicked.connect(self.change_theme)
        return_key = QShortcut(QKeySequence(Qt.Key.Key_Return), self)
        return_key.activated.connect(self.change_theme)

        ag.popups["themeChooser"] = self

    def mouseMoveEvent(self, e: QMouseEvent):
        if e.buttons() & Qt.MouseButton.LeftButton:
            pos_ = e.globalPosition().toPoint()
            dist = pos_ - self.start_pos
            if dist.manhattanLength() < 50:
                self.move(self.pos() + dist)
                e.accept()
            self.start_pos = pos_

    @pyqtSlot()
    def change_theme(self):
        theme = self.apply_theme()
        tug.save_app_setting(CurrentTheme=theme)
        self.rejected = False
        self.close()

    def apply_theme(self) -> str:
        theme = self.theme_list.currentItem().data(Qt.ItemDataRole.UserRole)
        styles = tug.prepare_styles(theme, self.log_theme.isChecked())
        QCoreApplication.instance().setStyleSheet(styles)
        self.apply_dyn_qss()
        self.set_icons()
        self.log_theme.setChecked(False)
        return theme

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

    def set_icons(self):
        def set_icons_from_list(buttons):
            for btn, *icons in buttons:
                if len(icons) > 1:
                    btn.setIcon(tug.get_icon(icons[btn.isChecked()]))
                else:
                    btn.setIcon(tug.get_icon(icons[0]))

        def set_checked_tool_btn():
            checkable_btn = {
                ag.appMode.DIR: ag.app.ui.btnDir,
                ag.appMode.FILTER: ag.app.ui.btnFilter,
                ag.appMode.FILTER_SETUP: ag.app.ui.btnFilterSetup,
            }
            mode = (ag.mode if ag.mode in
                    (ag.appMode.DIR, ag.appMode.FILTER, ag.appMode.FILTER_SETUP)
                    else ag.appMode(ag.curr_btn_id))
            btn = checkable_btn.get(mode, ag.app.ui.btnDir)
            btn.setIcon(tug.get_icon(btn.objectName(), 1))
            btn.setChecked(True)

        set_icons_from_list(ag.buttons.values())
        set_icons_from_list(ag.note_buttons)

        pix = tug.get_icon("busy", 0)
        ag.app.ui.busy.setPixmap(pix.pixmap(16, 16))
        set_checked_tool_btn()

    @pyqtSlot()
    def accept(self):
        self.rejected = False
        self.apply_theme()
        self.close()

    def set_themes(self):
        for key, theme in tug.themes.items():
            item = QListWidgetItem()
            item.setData(Qt.ItemDataRole.DisplayRole, theme["name"])
            item.setData(Qt.ItemDataRole.UserRole, key)
            if key == self.cur_theme:
                self.cur_row = self.theme_list.count()
            self.theme_list.addItem(item)
        self.theme_list.setCurrentRow(self.cur_row)

    def reject(self):
        if self.cur_theme != self.theme_list.currentItem().data(Qt.ItemDataRole.UserRole):
            self.theme_list.setCurrentRow(self.cur_row)
            self.apply_theme()

    def closeEvent(self, a0):
        ag.popups.pop("themeChooser")
        if self.rejected:
            self.reject()
        return super().closeEvent(a0)
