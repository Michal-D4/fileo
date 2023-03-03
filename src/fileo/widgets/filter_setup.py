from loguru import logger

from PyQt6.QtCore import Qt, QDate, QDateTime
from PyQt6.QtWidgets import QWidget

from core import app_globals as ag, icons, low_bk, db_ut
from widgets.ui_set_filter import Ui_filterSetup

def unix_date(ts: float) -> int:
    unix_epoch = 2440587.5   # julian date of 1970-01-01
    return int((ts - unix_epoch) * 86400)


class FilterSetup(QWidget):
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)

        self.ui = Ui_filterSetup()
        self.ui.setupUi(self)
        self.setStyleSheet(ag.dyn_qss["dialog"][0])
        self.ui.hrdFrame.setStyleSheet(ag.dyn_qss["dialog_hdr"][0])

        self.ui.after_date.setDisplayFormat("yyyy-MM-dd")
        self.ui.before_date.setDisplayFormat("yyyy-MM-dd")

        self.ui.btnDone.clicked.connect(self.done_clicked)
        self.ui.btnApply.clicked.connect(self.apply_clicked)
        self.ui.after.clicked.connect(self.after_changed)
        self.ui.before.clicked.connect(self.before_changed)
        self.ui.open_sel.clicked.connect(self.open_changed)
        self.ui.rating_sel.clicked.connect(self.rating_changed)
        self.ui.after_date.editingFinished.connect(self.changed_after_date)
        self.ui.before_date.editingFinished.connect(self.changed_before_date)

    def after_changed(self, st: bool):
        print(f"after_changed: {st=}")
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

    def before_changed(self, st: bool):
        print(f"before_changed: {st=}")
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
        print(f"changed_after_date")
        if self.ui.before.isChecked():
            self.ui.before_date.setMinimumDate(self.ui.after_date.date())

    def changed_before_date(self):
        print(f"changed_before_date")
        if self.ui.after.isChecked():
            self.ui.after_date.setMaximumDate(self.ui.before_date.date())

    def open_changed(self, st: bool):
        print(f"open_changed: {st=}")
        self.ui.open_edit.setEnabled(st)

    def rating_changed(self, st: bool):
        print(f"rating_changed: {st=}")
        self.ui.rating_edit.setEnabled(st)

    def done_clicked(self) -> bool:
        ag.signals_.filter_setup_closed.emit()
        return self.close()

    def apply_clicked(self):
        ag.signals_.user_action_signal.emit("filter_changed")

    def get_file_list(self):
        self.store_temp()
        self.checks['open_check'] = self.ui.open_sel.isChecked()
        self.checks['open_op'] = self.ui.open_cond.currentIndex()
        self.checks['open_val'] = self.ui.open_edit.value()
        self.checks['rating_check'] = self.ui.rating_sel.isChecked()
        self.checks['rating_op'] = self.ui.rating_cond.currentIndex()
        self.checks['rating_val'] = self.ui.rating_edit.value()
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
        if not self.checks['dir']:
            return
        idxs = ag.dir_list.selectionModel().selectedIndexes()
        self.checks['dir'] = (len(idxs) > 0)
        for idx in idxs:
            db_ut.save_to_temp('dir', idx.data(Qt.ItemDataRole.UserRole).id)
        db_ut.temp_files_dir()

    def store_tag_ids(self):
        id_list = ag.tag_list.get_selected_ids()
        if not id_list:
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
            for id in id_list[1:]:
                files_tag |= db_ut.get_files_tag(id)
        for file in files_tag:
            db_ut.save_to_temp('file_tag', file)
        self.checks['tag'] = (len(files_tag) > 0)

    def store_ext_ids(self):
        ext_list = ag.ext_list.get_selected_ids()
        for id in ext_list:
            db_ut.save_to_temp('ext', id)
        self.checks['ext'] = (len(ext_list) > 0)

    def store_author_ids(self):
        authors = ag.author_list.get_selected_ids()
        for id in authors:
            db_ut.save_to_temp('author', id)
        self.checks['author'] = (len(authors) > 0)

    def save_filter_setting(self):
        print(self.geometry())

    def dir_selection_changed(self):
        indexes = ag.dir_list.selectedIndexes()
        dirs = []
        for idx in indexes:
            dirs.append(f"[{idx.data(Qt.ItemDataRole.DisplayRole)}]")
        dirs.sort(key=str.lower)
        self.ui.dir_list.setPlainText(', '.join(dirs))
        if ag.mode is ag.appMode.FILTER and self.ui.selected_dir.isChecked():
            ag.signals_.user_action_signal.emit("filter_changed")

    def tag_selection_changed(self, tags: list[str]):
        self.ui.tag_list.setPlainText(', '.join([f"[{tag}]" for tag in tags]))
        if ag.mode is ag.appMode.FILTER and self.ui.selected_tag.isChecked():
            ag.signals_.user_action_signal.emit("filter_changed")

    def ext_selection_changed(self, exts: list[str]):
        self.ui.ext_list.setPlainText(', '.join([f"[{ext}]" for ext in exts]))
        if ag.mode is ag.appMode.FILTER and self.ui.selected_ext.isChecked():
            ag.signals_.user_action_signal.emit("filter_changed")

    def author_selection_changed(self, authors: list[str]):
        self.ui.author_list.setPlainText(
            ', '.join([f"[{author}]" for author in authors]))
        if ag.mode is ag.appMode.FILTER and self.ui.selected_author.isChecked():
            ag.signals_.user_action_signal.emit("filter_changed")

    def save_filter_settings(self):
        settings = {
            "DIR_CHECK": self.ui.selected_dir.isChecked(),
            "TAG_CHECK": self.ui.selected_tag.isChecked(),
            "IS_ALL": self.ui.all_btn.isChecked(),
            "EXT_CHECK": self.ui.selected_ext.isChecked(),
            "AUTHOR_CHECK": self.ui.selected_author.isChecked(),
            "OPEN_CHECK": self.ui.open_sel.isChecked(),
            "OPEN_OP": self.ui.open_cond.currentIndex(),
            "OPEN_VAL": self.ui.open_edit.value(),
            "RATING_CHECK": self.ui.rating_sel.isChecked(),
            "RATING_OP": self.ui.rating_cond.currentIndex(),
            "RATING_VAL": self.ui.rating_edit.value(),
            "DATE_TYPE": self.ui.date_type.currentIndex(),
            "AFTER": self.ui.after.isChecked(),
            "BEFORE": self.ui.before.isChecked(),
            "AFTER_DATE": self.ui.after_date.date().toJulianDay(),
            "BEFORE_DATE": self.ui.before_date.date().toJulianDay(),
        }
        low_bk.save_settings(**settings)

    def restore_filter_settings(self):
        self.ui.selected_dir.setChecked(low_bk.get_setting("DIR_CHECK", False))
        self.ui.selected_tag.setChecked(low_bk.get_setting("TAG_CHECK", False))
        self.ui.all_btn.setChecked(low_bk.get_setting("IS_ALL", False))
        self.ui.any_btn.setChecked(not low_bk.get_setting("IS_ALL", False))
        self.ui.selected_ext.setChecked(low_bk.get_setting("EXT_CHECK", False))
        self.ui.selected_author.setChecked(low_bk.get_setting("AUTHOR_CHECK", False))
        self.ui.open_sel.setChecked(low_bk.get_setting("OPEN_CHECK", False))
        self.ui.open_cond.setCurrentIndex(low_bk.get_setting("OPEN_OP", 0))
        self.ui.open_edit.setValue(low_bk.get_setting("OPEN_VAL", 0))
        self.ui.rating_sel.setChecked(low_bk.get_setting("RATING_CHECK", False))
        self.ui.rating_cond.setCurrentIndex(low_bk.get_setting("RATING_OP", 0))
        self.ui.rating_edit.setValue(low_bk.get_setting("RATING_VAL", 0))
        self.ui.date_type.setCurrentIndex(low_bk.get_setting("DATE_TYPE", 0))
        self.ui.after.setChecked(low_bk.get_setting("AFTER", False))
        self.ui.before.setChecked(low_bk.get_setting("BEFORE", False))
        self.ui.after_date.setDate(QDate.fromJulianDay(low_bk.get_setting("AFTER_DATE", 0)))
        self.ui.before_date.setDate(QDate.fromJulianDay(low_bk.get_setting("BEFORE_DATE", 0)))
