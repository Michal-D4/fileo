# from loguru import logger
from PyQt6.QtCore import Qt, QDate, QPoint
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtWidgets import QWidget

from ..core import app_globals as ag, db_ut
from .ui_set_filter import Ui_filterSetup
from .. import tug

UNIX_EPOCH = 2440588   # julian date of 1970-01-01

def unix_date(ts: float) -> int:
    return int((ts - UNIX_EPOCH) * 86400)


class FilterSetup(QWidget):
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)

        self.single_folder = False
        self.start_pos = QPoint()

        self.ui = Ui_filterSetup()
        self.ui.setupUi(self)
        self.ui.ico.setPixmap(tug.get_icon('ico_app').pixmap(24, 24))
        self.ui.after_date.setCalendarPopup(True)
        self.ui.before_date.setCalendarPopup(True)
        ttls = tug.qss_params['$FoldTitles'].lower()
        titles = ttls.split(',')
        self.ui.selected_dir.setText(titles[0])
        self.ui.selected_tag.setText(titles[1])
        self.ui.selected_ext.setText(titles[2])
        self.ui.selected_author.setText(titles[3])

        self.ui.after_date.setDisplayFormat("yyyy-MM-dd")
        self.ui.before_date.setDisplayFormat("yyyy-MM-dd")

        self.ui.selected_dir.checkStateChanged.connect(self.dir_check)
        self.ui.no_folder.checkStateChanged.connect(self.no_dir_check)
        self.ui.selected_tag.checkStateChanged.connect(self.toggle_tag_check)
        self.ui.btnDone.clicked.connect(self.done_clicked)
        self.ui.btnApply.clicked.connect(self.apply_clicked)
        self.ui.after.clicked.connect(self.after_clicked)
        self.ui.before.clicked.connect(self.before_clicked)
        self.ui.open_sel.clicked.connect(self.open_clicked)
        self.ui.rating_sel.clicked.connect(self.rating_clicked)
        self.ui.after_date.editingFinished.connect(self.changed_after_date)
        self.ui.before_date.editingFinished.connect(self.changed_before_date)
        ag.signals_.author_widget_title.connect(lambda ttl: self.ui.selected_author.setText(ttl.lower()))

        self.mouseMoveEvent = self.move_self

    def move_self(self, e: QMouseEvent):
        if e.buttons() == Qt.MouseButton.LeftButton:
            pos_ = e.globalPosition().toPoint()
            dist = pos_ - self.start_pos
            if dist.manhattanLength() < 50:
                self.move(self.pos() + dist)
                e.accept()
            self.start_pos = pos_

    def dir_check(self, state: Qt.CheckState):
        if state is Qt.CheckState.Checked:
            self.ui.no_folder.setCheckState(Qt.CheckState.Unchecked)

    def no_dir_check(self, state: Qt.CheckState):
        if state is Qt.CheckState.Checked:
            self.ui.selected_dir.setCheckState(Qt.CheckState.Unchecked)

    def toggle_tag_check(self, state: Qt.CheckState):
        self.ui.all_btn.setEnabled(state is Qt.CheckState.Checked)
        self.ui.any_btn.setEnabled(state is Qt.CheckState.Checked)

    def is_single_folder(self) -> bool:
        return self.single_folder

    def after_clicked(self, st: bool):
        self.ui.after_date.setEnabled(st)
        if not st:
            self.ui.before_date.clearMinimumDate()
            return
        if self.ui.before.isChecked():
            if self.ui.after_date.date() > self.ui.before_date.date():
                self.ui.after_date.setDate(self.ui.before_date.date())
            self.ui.after_date.setMaximumDate(self.ui.before_date.date())
        else:
            self.ui.after_date.clearMaximumDate()

    def before_clicked(self, st: bool):
        self.ui.before_date.setEnabled(st)
        if not st:
            self.ui.after_date.clearMaximumDate()
            return
        if self.ui.after.isChecked():
            if self.ui.before_date.date() < self.ui.after_date.date():
                self.ui.before_date.setDate(self.ui.after_date.date())
            self.ui.before_date.setMinimumDate(self.ui.after_date.date())
        else:
            self.ui.before_date.clearMinimumDate()

    def changed_after_date(self):
        if self.ui.before.isChecked():
            self.ui.before_date.setMinimumDate(self.ui.after_date.date())

    def changed_before_date(self):
        if self.ui.after.isChecked():
            self.ui.after_date.setMaximumDate(self.ui.before_date.date())

    def open_clicked(self, st: bool):
        self.ui.open_edit.setEnabled(st)

    def rating_clicked(self, st: bool):
        self.ui.rating_edit.setEnabled(st)

    def done_clicked(self) -> bool:
        ag.signals_.filter_setup_closed.emit()
        return self.close()

    def apply_clicked(self):
        ag.signals_.user_signal.emit("filter_changed")

    def get_file_list(self):
        self.store_temp()
        self.checks['open_check'] = self.ui.open_sel.isChecked()
        self.checks['open_op'] = self.ui.open_cond.currentIndex()
        self.checks['open_val'] = self.ui.open_edit.text()
        self.checks['rating_check'] = self.ui.rating_sel.isChecked()
        self.checks['rating_op'] = self.ui.rating_cond.currentIndex()
        self.checks['rating_val'] = self.ui.rating_edit.text()
        self.checks['date'] = self.ui.date_type.currentText()
        self.checks['after'] = self.ui.after.isChecked()
        self.checks['before'] = self.ui.before.isChecked()
        # date interval includes both ends: 'after' and 'before'
        self.checks['date_after'] = unix_date(self.ui.after_date.date().toJulianDay())
        self.checks['date_before'] = unix_date(self.ui.before_date.date().addDays(1).toJulianDay())
        return db_ut.filter_files(self.checks)

    def store_temp(self):
        self.checks = {
            'dir': self.ui.selected_dir.isChecked(),
            'no_dir': self.ui.no_folder.isChecked(),
            'tag': self.ui.selected_tag.isChecked(),
            'ext': self.ui.selected_ext.isChecked(),
            'author': self.ui.selected_author.isChecked(),
        }
        db_ut.clear_temp()
        self.store_dir_ids()
        if self.checks['tag']:
            self.store_tag_ids()
        if self.checks['ext']:
            self.store_ext_ids()
        if self.checks['author']:
            self.store_author_ids()

    def store_dir_ids(self):
        if not self.checks['dir']:   # if any folder is not selected
            self.single_folder = False
            if self.checks['no_dir']:
                db_ut.temp_files_no_dir()
            return
        idxs = ag.dir_list.selectionModel().selectedIndexes()
        self.single_folder = (len(idxs) == 1)
        dirs = []
        for idx in idxs:
            dirs.append((idx.data(Qt.ItemDataRole.UserRole).id,))
        db_ut.temp_files_dir(dirs, self.ui.subDirs.isChecked())

    def store_tag_ids(self):
        id_list = ag.tag_list.get_selected_ids()
        if not id_list:   # if any tag is not selected
            self.checks['tag'] = False
            return
        if self.ui.all_btn.isChecked():
            files_tag = db_ut.get_files_tag(id_list[0])
            for id in id_list[1:]:
                files_tag &= db_ut.get_files_tag(id)
                if not files_tag:
                    break
        else:   # self.ui.any_btn.isChecked()
            files_tag = set()
            for id in id_list:
                files_tag |= db_ut.get_files_tag(id)
        for file in files_tag:
            db_ut.save_to_temp('file_tag', file)

    def store_ext_ids(self):
        ext_list = ag.ext_list.get_selected_ids()
        if not ext_list:   # if any extension is not selected
            self.checks['ext'] = False
            return
        for id in ext_list:
            db_ut.save_to_temp('ext', id)

    def store_author_ids(self):
        authors = ag.author_list.get_selected_ids()
        if not authors:    # if any author is not selected
            self.checks['author'] = False
            return
        for id in authors:
            db_ut.save_to_temp('author', id)

    def set_dir_list(self):
        indexes = ag.dir_list.selectedIndexes()
        dirs = []
        for idx in indexes:
            dirs.append(f"[{idx.data(Qt.ItemDataRole.DisplayRole)}]")
        dirs.sort(key=str.lower)
        self.ui.dir_list.setPlainText(', '.join(dirs))

    def dir_selection_changed(self):
        self.set_dir_list()
        if ag.mode is ag.appMode.FILTER and self.ui.selected_dir.isChecked():
            ag.signals_.user_signal.emit("filter_changed")

    def set_tag_list(self, tags: list[str]):
        self.ui.tag_list.setPlainText(', '.join([f"[{tag}]" for tag in tags]))

    def tag_selection_changed(self, tags: list[str]):
        self.set_tag_list(tags)
        if ag.mode is ag.appMode.FILTER and self.ui.selected_tag.isChecked():
            ag.signals_.user_signal.emit("filter_changed")

    def set_ext_list(self, exts: list[str]):
        self.ui.ext_list.setPlainText(', '.join([f"[{ext}]" for ext in exts]))

    def ext_selection_changed(self, exts: list[str]):
        self.set_ext_list(exts)
        if ag.mode is ag.appMode.FILTER and self.ui.selected_ext.isChecked():
            ag.signals_.user_signal.emit("filter_changed")

    def set_author_list(self, authors: list[str]):
        self.ui.author_list.setPlainText(
            ', '.join([f"[{author}]" for author in authors]))

    def author_selection_changed(self, authors: list[str]):
        self.set_author_list(authors)
        if ag.mode is ag.appMode.FILTER and self.ui.selected_author.isChecked():
            ag.signals_.user_signal.emit("filter_changed")

    def save_filter_settings(self):
        settings = {
            "DIR_CHECK": self.ui.selected_dir.isChecked(),
            "SUB_DIR_CHECK": self.ui.subDirs.isChecked(),
            "TAG_CHECK": self.ui.selected_tag.isChecked(),
            "IS_ALL": self.ui.all_btn.isChecked(),
            "EXT_CHECK": self.ui.selected_ext.isChecked(),
            "AUTHOR_CHECK": self.ui.selected_author.isChecked(),
            "OPEN_CHECK": self.ui.open_sel.isChecked(),
            "OPEN_OP": self.ui.open_cond.currentIndex(),
            "OPEN_VAL": self.ui.open_edit.text(),
            "RATING_CHECK": self.ui.rating_sel.isChecked(),
            "RATING_OP": self.ui.rating_cond.currentIndex(),
            "RATING_VAL": self.ui.rating_edit.text(),
            "DATE_TYPE": self.ui.date_type.currentIndex(),
            "AFTER": self.ui.after.isChecked(),
            "BEFORE": self.ui.before.isChecked(),
            "AFTER_DATE": self.ui.after_date.date().toJulianDay(),
            "BEFORE_DATE": self.ui.before_date.date().toJulianDay(),
        }
        ag.save_settings(**settings)

    def restore_filter_settings(self):
        self.ui.selected_dir.setChecked(ag.get_setting("DIR_CHECK", False))
        self.ui.subDirs.setChecked(ag.get_setting("SUB_DIR_CHECK", False))
        self.ui.selected_tag.setChecked(ag.get_setting("TAG_CHECK", False))
        is_all = ag.get_setting("IS_ALL", False)
        self.ui.all_btn.setChecked(is_all)
        self.ui.any_btn.setChecked(not is_all)
        self.ui.selected_ext.setChecked(ag.get_setting("EXT_CHECK", False))
        self.ui.selected_author.setChecked(ag.get_setting("AUTHOR_CHECK", False))
        self.ui.open_sel.setChecked(ag.get_setting("OPEN_CHECK", False))
        self.ui.open_cond.setCurrentIndex(ag.get_setting("OPEN_OP", 0))
        self.ui.open_edit.setText(str(ag.get_setting("OPEN_VAL", "0")))
        self.ui.rating_sel.setChecked(ag.get_setting("RATING_CHECK", False))
        self.ui.rating_cond.setCurrentIndex(ag.get_setting("RATING_OP", 0))
        self.ui.rating_edit.setText(str(ag.get_setting("RATING_VAL", "0")))
        self.ui.date_type.setCurrentIndex(ag.get_setting("DATE_TYPE", 0))
        self.ui.after.setChecked(ag.get_setting("AFTER", False))
        self.ui.before.setChecked(ag.get_setting("BEFORE", False))
        cur_date = QDate.currentDate().toJulianDay()
        after = ag.get_setting("AFTER_DATE", cur_date)
        if after == 2361222:        # 'Thu Sep 14 1752'
            after = cur_date
        before = ag.get_setting("BEFORE_DATE", cur_date)
        if before == 2361222:       # 'Thu Sep 14 1752'
            before = cur_date
        self.ui.after_date.setDate(QDate.fromJulianDay(after))
        self.ui.before_date.setDate(QDate.fromJulianDay(before))

        self.set_tag_list(ag.tag_list.get_selected())
        self.set_ext_list(ag.ext_list.get_selected())
        self.set_author_list(ag.author_list.get_selected())
        self.set_dir_list()
