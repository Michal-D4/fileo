# from loguru import logger
from PyQt6.QtCore import Qt, QDate, QPoint, QSize, QDateTime, QTime, QTimeZone
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtWidgets import QWidget

from ..core import app_globals as ag, db_ut
from .ui_set_filter import Ui_filterSetup
from .. import tug

UNIX_EPOCH = 2440588   # julian date of 1970-01-01
DLG_SIZE = QSize(502, 496)


class FilterSetup(QWidget):
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)

        self.single_folder = False
        self.start_pos = QPoint()
        self.checked_btn = -1

        self.ui = Ui_filterSetup()
        self.ui.setupUi(self)
        self.ui.selected_tag.setMinimumWidth(60)
        self.init_how_added()
        self.set_rating_field()
        self.set_publish_field()
        self.ui.note_date_type.setVisible(self.ui.date_type.currentData(Qt.ItemDataRole.UserRole) == 'note_date')

        self.ui.ico.setPixmap(tug.get_icon('ico_app').pixmap(24, 24))
        self.ui.after_date.setCalendarPopup(True)
        self.ui.before_date.setCalendarPopup(True)
        ttls = tug.qss_params['$FoldTitles']
        titles = [x.lower() for x in ttls]
        self.ui.selected_dir.setText(titles[0])
        self.ui.selected_tag.setText(titles[1])
        self.ui.selected_ext.setText(titles[2])
        self.ui.selected_author.setText(titles[3])

        self.ui.after_date.setDisplayFormat("yyyy-MM-dd")
        self.ui.before_date.setDisplayFormat("yyyy-MM-dd")

        self.ui.file_buttons.idClicked.connect(self.file_button_clicked)
        self.ui.selected_tag.checkStateChanged.connect(self.toggle_tag_check)
        self.ui.after.clicked.connect(self.after_clicked)
        self.ui.before.clicked.connect(self.before_clicked)
        self.ui.open_sel.clicked.connect(self.open_clicked)
        self.ui.rating_sel.clicked.connect(self.rating_clicked)
        self.ui.date_type.currentIndexChanged.connect(
            lambda: self.ui.note_date_type.setVisible(
                self.ui.date_type.currentData(Qt.ItemDataRole.UserRole) == 'note_date')
        )
        self.ui.after_date.editingFinished.connect(self.changed_after_date)
        self.ui.before_date.editingFinished.connect(self.changed_before_date)
        ag.signals.author_widget_title.connect(lambda ttl: self.ui.selected_author.setText(ttl.lower()))

        self.ui.btnDone.clicked.connect(self.done_clicked)
        self.ui.btnApply.clicked.connect(self.apply_clicked)

        self.mouseMoveEvent = self.move_self
        self.font_changed(tug.get_app_setting('FONT_SIZE', '10pt'))
        ag.signals.font_size_changed.connect(self.font_changed)

    def set_ed_fields(self, field: str):
        {'3': self.set_rating_field, '8': self.set_publish_field}[field]()

    def set_rating_field(self):
        is_int = tug.qss_params['$FieldTypes'][3] == "int"
        self.ui.rating_sel.setVisible(is_int)
        self.ui.rating_frame.setVisible(is_int)

        if is_int:
            self.ui.rating_sel.setText(tug.qss_params['$FileListFields'][3])

    def set_publish_field(self):
        self.ui.date_type.clear()
        db_flds = {1: "added", 2: "opened", 5: "modified", 8: "published", 9: "note_date"}
        date_ids = (1, 2, 5, 8, 9,) if tug.qss_params['$FieldTypes'][8] == "date" else (1, 2, 5, 9,)
        for i in date_ids:
            self.ui.date_type.addItem(tug.qss_params['$FileListFields'][i], userData=db_flds[i])
        self.ui.date_type.setCurrentIndex(ag.get_db_setting("DATE_TYPE", 0))

    def init_how_added(self):
        items = ("", "scan file system", "drag from file system", "import file list",
                 "drag from another instance    ", "created here")
        for it in ag.fileSource:
            self.ui.how_added.addItem(items[it.value], userData=it.value)

    def file_button_clicked(self, id: int):
        if self.checked_btn != -1:
            self.ui.file_buttons.button(self.checked_btn).setChecked(False)
        self.checked_btn = -1 if self.checked_btn == id else id

    def font_changed(self, font_size: str):
        self.cur_size = DLG_SIZE * tug.SIZE_RATIO[font_size]
        self.ui.selected_tag.setMinimumWidth(int(60 * tug.SIZE_RATIO[font_size]))
        self.ui.dlg_frame.setMinimumSize(self.cur_size)
        self.adjustSize()

    def move_self(self, e: QMouseEvent):
        if e.buttons() == Qt.MouseButton.LeftButton:
            pos_ = e.globalPosition().toPoint()
            dist = pos_ - self.start_pos
            if dist.manhattanLength() < 50:
                self.move(self.pos() + dist)
                e.accept()
            self.start_pos = pos_

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

    def done_clicked(self):
        ag.signals.filter_setup_closed.emit()
        self.close()

    def apply_clicked(self):
        ag.save_db_settings(FILTER_FILE_ID=0)
        ag.signals.user_signal.emit("filter_changed")

    def get_file_list(self):
        self.store_temp()
        self.checks['open_check'] = self.ui.open_sel.isChecked()
        self.checks['open_op'] = self.ui.open_cond.currentIndex()
        self.checks['open_val'] = self.ui.open_edit.text()
        self.checks['rating_check'] = self.ui.rating_sel.isChecked()
        self.checks['rating_op'] = self.ui.rating_cond.currentIndex()
        self.checks['rating_val'] = self.ui.rating_edit.text()
        return db_ut.filter_files(self.checks)

    def store_temp(self):
        self.checks = {
            'dir': self.ui.selected_dir.isChecked(),
            'sub_dir': self.ui.subDirs.isChecked(),
            'no_dir': self.ui.no_folder.isChecked(),
            'add_method': self.ui.add_method.isChecked(),
            'tag': self.ui.selected_tag.isChecked(),
            'ext': self.ui.selected_ext.isChecked(),
            'author': self.ui.selected_author.isChecked(),
            'date': self.ui.date_type.currentData(Qt.ItemDataRole.UserRole),
            'note_date': self.ui.note_date_type.currentText(),
            'after': self.ui.after.isChecked(),
            'before': self.ui.before.isChecked(),
            'date_after': QDateTime(self.ui.after_date.date(), QTime(),
                                    QTimeZone(QTimeZone.Initialization.UTC)).toSecsSinceEpoch(),
            'date_before': QDateTime(self.ui.before_date.date().addDays(1), QTime(),
                                     QTimeZone(QTimeZone.Initialization.UTC)).toSecsSinceEpoch(),
        }
        if self.checks['add_method']:
            self.checks['how_added'] = self.ui.how_added.currentData(Qt.ItemDataRole.UserRole)

        db_ut.clear_temp()
        self.store_dir_files()
        if self.checks['tag']:
            self.store_tag_files()
        if self.checks['ext']:
            self.store_ext_ids()
        if self.checks['author']:
            self.store_author_ids()
        self.store_note_date_files()

    def store_dir_files(self):
        idxs = ag.dir_list.selectionModel().selectedIndexes()
        self.single_folder = (len(idxs) == 1)
        dirs = []
        for idx in idxs:
            dirs.append((idx.data(Qt.ItemDataRole.UserRole).dir_id,))
        self.single_folder = db_ut.temp_files_dir(dirs, self.checks)

    def store_tag_files(self):
        tag_ids = ag.tag_list.get_selected_ids()
        if not tag_ids:              # if any tag is not selected
            self.checks['tag'] = False
            return
        if self.ui.all_btn.isChecked():
            tag_files = db_ut.get_tag_files(tag_ids[0])   # tag_files: set
            for id in tag_ids[1:]:
                tag_files &= db_ut.get_tag_files(id)
                if not tag_files:
                    break
        else:                        # self.ui.any_btn.isChecked()
            tag_files = set()
            for id in tag_ids:
                tag_files |= db_ut.get_tag_files(id)
        for file in tag_files:
            db_ut.save_to_temp('file_tag', file)

    def store_note_date_files(self):
        self.checks['note date is set'] = (
            self.checks['date'] == "note_date" and
            (self.checks['after'] or self.checks['before'])
        )
        if not self.checks['note date is set']:
            return
        files = db_ut.get_note_date_files(self.checks)
        for file in files:
            db_ut.save_to_temp('note_date_files', file[0])

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
            self.apply_clicked()

    def set_tag_list(self, tags: list[str]):
        self.ui.tag_list.setPlainText(', '.join([f"[{tag}]" for tag in tags]))

    def tag_selection_changed(self, tags: list[str]):
        self.set_tag_list(tags)
        if ag.mode is ag.appMode.FILTER and self.ui.selected_tag.isChecked():
            self.apply_clicked()

    def set_ext_list(self, exts: list[str]):
        self.ui.ext_list.setPlainText(', '.join([f"[{ext}]" for ext in exts]))

    def ext_selection_changed(self, exts: list[str]):
        self.set_ext_list(exts)
        if ag.mode is ag.appMode.FILTER and self.ui.selected_ext.isChecked():
            self.apply_clicked()

    def set_author_list(self, authors: list[str]):
        self.ui.author_list.setPlainText(
            ', '.join([f"[{author}]" for author in authors]))

    def author_selection_changed(self, authors: list[str]):
        self.set_author_list(authors)
        if ag.mode is ag.appMode.FILTER and self.ui.selected_author.isChecked():
            self.apply_clicked()

    def save_filter_settings(self):
        settings = {
            "DIR_CHECK": self.ui.selected_dir.isChecked(),
            "SUB_DIR_CHECK": self.ui.subDirs.isChecked(),
            "NO_FOLDER": self.ui.no_folder.isChecked(),
            "USE_ADD_METHOD": self.ui.add_method.isChecked(),
            "TAG_CHECK": self.ui.selected_tag.isChecked(),
            "IS_ALL": self.ui.all_btn.isChecked(),
            "HOW_ADDED": self.ui.how_added.currentIndex(),
            "EXT_CHECK": self.ui.selected_ext.isChecked(),
            "AUTHOR_CHECK": self.ui.selected_author.isChecked(),
            "OPEN_CHECK": self.ui.open_sel.isChecked(),
            "OPEN_OP": self.ui.open_cond.currentIndex(),
            "OPEN_VAL": self.ui.open_edit.text(),
            "RATING_CHECK": self.ui.rating_sel.isChecked(),
            "RATING_OP": self.ui.rating_cond.currentIndex(),
            "RATING_VAL": self.ui.rating_edit.text(),
            "DATE_TYPE": self.ui.date_type.currentIndex(),
            "NOTE_DATE_TYPE": self.ui.note_date_type.currentIndex(),
            "AFTER": self.ui.after.isChecked(),
            "BEFORE": self.ui.before.isChecked(),
            "AFTER_DATE": self.ui.after_date.date().toJulianDay(),
            "BEFORE_DATE": self.ui.before_date.date().toJulianDay(),
        }
        ag.save_db_settings(**settings)

    def restore_filter_settings(self):
        self.ui.selected_dir.setChecked(ag.get_db_setting("DIR_CHECK", False))
        if self.ui.selected_dir.isChecked():
            self.checked_btn = self.ui.file_buttons.id(self.ui.selected_dir)
        self.ui.subDirs.setChecked(ag.get_db_setting("SUB_DIR_CHECK", False))
        self.ui.no_folder.setChecked(ag.get_db_setting("NO_FOLDER", False))
        if self.ui.no_folder.isChecked():
            self.checked_btn = self.ui.file_buttons.id(self.ui.no_folder)
        self.ui.add_method.setChecked(ag.get_db_setting("USE_ADD_METHOD", False))
        self.ui.selected_tag.setChecked(ag.get_db_setting("TAG_CHECK", False))
        is_all = ag.get_db_setting("IS_ALL", False)
        self.ui.all_btn.setChecked(is_all)
        self.ui.any_btn.setChecked(not is_all)
        self.ui.how_added.setCurrentIndex(ag.get_db_setting("HOW_ADDED", 0))
        self.ui.selected_ext.setChecked(ag.get_db_setting("EXT_CHECK", False))
        self.ui.selected_author.setChecked(ag.get_db_setting("AUTHOR_CHECK", False))
        self.ui.open_sel.setChecked(ag.get_db_setting("OPEN_CHECK", False))
        self.ui.open_cond.setCurrentIndex(ag.get_db_setting("OPEN_OP", 0))
        self.ui.open_edit.setText(str(ag.get_db_setting("OPEN_VAL", "0")))
        self.ui.rating_sel.setChecked(ag.get_db_setting("RATING_CHECK", False))
        self.ui.rating_cond.setCurrentIndex(ag.get_db_setting("RATING_OP", 0))
        self.ui.rating_edit.setText(str(ag.get_db_setting("RATING_VAL", "0")))
        self.ui.date_type.setCurrentIndex(ag.get_db_setting("DATE_TYPE", 0))
        self.ui.note_date_type.setCurrentIndex(ag.get_db_setting("NOTE_DATE_TYPE", 0))
        self.ui.after.setChecked(ag.get_db_setting("AFTER", False))
        self.ui.before.setChecked(ag.get_db_setting("BEFORE", False))
        cur_date = QDate.currentDate().toJulianDay()
        after = ag.get_db_setting("AFTER_DATE", cur_date)
        if after == 2361222:        # 'Thu Sep 14 1752'
            after = cur_date
        before = ag.get_db_setting("BEFORE_DATE", cur_date)
        if before == 2361222:       # 'Thu Sep 14 1752'
            before = cur_date
        self.ui.after_date.setDate(QDate.fromJulianDay(after))
        self.ui.before_date.setDate(QDate.fromJulianDay(before))

        self.set_tag_list(ag.tag_list.get_selected())
        self.set_ext_list(ag.ext_list.get_selected())
        self.set_author_list(ag.author_list.get_selected())
