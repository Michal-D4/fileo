# from loguru import logger
from PyQt6.QtCore import Qt, QDate, QPoint, QSize, QDateTime, QTime
from PyQt6.QtGui import QMouseEvent, QIntValidator
from PyQt6.QtWidgets import QWidget, QStackedWidget, QLineEdit

from ..core import app_globals as ag, db_ut
from .ui_set_filter import Ui_filterSetup
from .ui_dt_editor import Ui_dtSetter
from .ui_fltr_gen_page import Ui_pageGen
from .ui_fltr_adv_page import Ui_pageAdv
from .. import tug

DLG_SIZE = QSize(535, 416)
DATE_FMT = "yyyy-MM-dd HH:mm"

class dateTimeSetter(QWidget, Ui_dtSetter):
    def __init__(self, target: QLineEdit, parent: QWidget = None):
        super().__init__(parent)

        self.setupUi(self)
        self.target = target
        self.setData()

        self.ok.clicked.connect(self.save_new)
        self.cancel.clicked.connect(self.close)
        ag.popups["dtSetter"] = self

    def setData(self):
        date_str = self.target.text()
        date_ = QDate.fromString(date_str[:10], "yyyy-MM-dd")
        self.dateEdit.setDate(date_ if date_ else QDate.currentDate())
        time_ = QTime.fromString(date_str[11:], "HH:mm")
        self.timeEdit.setTime(time_ if time_ else QTime(0, 0) if self.target.objectName() == "date_after" else QTime(23, 59, 59))

    def save_new(self):
        dd = self.dateEdit.date(); tt = self.timeEdit.time()  # noqa: E702
        self.target.setText(QDateTime(dd, tt).toString(DATE_FMT))
        self.close()

    def closeEvent(self, a0):
        ag.popups.pop("dtSetter")
        return super().closeEvent(a0)

class genPage(QWidget, Ui_pageGen):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        self.setupUi(self)

class advPage(QWidget, Ui_pageAdv):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

        self.setupUi(self)

class FilterSetup(QWidget):
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)

        self.single_folder = False
        self.start_pos = QPoint()
        self.checked_btn = -1
        self.date_selector = -1

        self.ui = Ui_filterSetup()
        self.ui.setupUi(self)

        self.gen = genPage(self)
        self.adv = advPage(self)
        self.set_pages_style()

        self.set_pages()
        self.cur_page = 1
        self.toggle_page(0)

        self.adv.not_older_nn.setValidator(QIntValidator())

        self.gen.selected_tag.setMinimumWidth(60)
        self.init_how_added()
        self.set_rating_field()
        self.set_publish_field()
        self.adv.note_date_type.setVisible(self.adv.date_type.currentData(Qt.ItemDataRole.UserRole) == 'note_date')

        self.ui.ico.setPixmap(tug.get_icon('ico_app').pixmap(24, 24))

        titles = tug.qss_params['$FoldTitles']
        self.gen.selected_dir.setText(titles[0].lower())
        self.gen.selected_tag.setText(titles[1].lower())
        self.gen.selected_ext.setText(titles[2].lower())
        self.gen.selected_author.setText(titles[3].lower())

        self.adv.date_selectors.idClicked.connect(self.date_selector_clicked)
        self.gen.file_buttons.idClicked.connect(self.file_button_clicked)
        self.gen.selected_tag.checkStateChanged.connect(self.toggle_tag_check)
        self.adv.open_sel.clicked.connect(self.open_clicked)
        self.adv.rating_sel.clicked.connect(self.rating_clicked)
        self.adv.date_type.currentIndexChanged.connect(lambda: self.adv.note_date_type.setVisible(
                self.adv.date_type.currentData(Qt.ItemDataRole.UserRole) == 'note_date')
        )
        ag.signals.author_widget_title.connect(lambda ttl: self.gen.selected_author.setText(ttl.lower()))

        self.ui.btnDone.clicked.connect(self.done_clicked)
        self.ui.btnApply.clicked.connect(self.apply_clicked)

        ag.signals.font_size_changed.connect(self.font_changed)

    def set_pages(self):
        self.filter_pages = QStackedWidget(self)
        self.filter_pages.setObjectName("filter_pages")

        self.filter_pages.addWidget(self.gen)
        self.filter_pages.addWidget(self.adv)

        self.ui.verticalLayout_4.addWidget(self.filter_pages)

        self.ui.gen_lab.mousePressEvent = self.gen_page_select
        self.ui.adv_lab.mousePressEvent = self.adv_page_select

        self.adv.after_btn.setIcon(tug.get_icon("down3"))
        self.adv.before_btn.setIcon(tug.get_icon("down3"))
        self.adv.after_btn.clicked.connect(self.set_date_beg)
        self.adv.before_btn.clicked.connect(self.set_date_end)

    def set_pages_style(self):
        self.gen.setStyleSheet(tug.get_dyn_qss("gen_page"))
        self.adv.setStyleSheet(tug.get_dyn_qss("adv_page"))

    def set_date_beg(self):
        self.set_date(self.adv.date_after)

    def set_date_end(self):
        self.set_date(self.adv.date_before)

    def set_date(self, target: QLineEdit):
        if "dtSetter" in ag.popups:
            return
        setter = dateTimeSetter(target, self)
        pos = self.mapFromGlobal(target.mapToGlobal(target.pos()))
        setter.move(pos.x()-95, pos.y()+15)
        setter.show()

    def gen_page_select(self, e: QMouseEvent):
        self.toggle_page(0)

    def adv_page_select(self, e: QMouseEvent):
        self.toggle_page(1)

    def set_selectors_style(self):
        labs = (self.ui.gen_lab, self.ui.adv_lab)
        labs[self.cur_page].setStyleSheet(tug.get_dyn_qss('active_selector'))
        labs[(self.cur_page+1) % 2].setStyleSheet(tug.get_dyn_qss('passive_selector'))

    def toggle_page(self, idx: int):
        if idx == self.cur_page:
            return

        self.cur_page = idx
        self.set_selectors_style()
        self.filter_pages.setCurrentIndex(idx)

    def set_ed_fields(self, field: str):
        {'3': self.set_rating_field, '8': self.set_publish_field}[field]()

    def set_rating_field(self):
        is_int = ag.get_db_setting('FieldTypes', tug.qss_params['$FieldTypes'])[3] == "int"
        self.adv.rating_sel.setVisible(is_int)
        self.adv.rating_cond.setVisible(is_int)
        self.adv.rating_edit.setVisible(is_int)

        if is_int:
            self.adv.rating_sel.setText(
                ag.get_db_setting('FileListFields', tug.qss_params['$FileListFields'])[3]
            )

    def set_publish_field(self):
        self.adv.date_type.clear()
        db_flds = {1: "added", 2: "opened", 5: "modified", 8: "published", 9: "note_date"}
        fields = ag.get_db_setting('FileListFields', tug.qss_params['$FileListFields'])
        types = ag.get_db_setting('FieldTypes', tug.qss_params['$FieldTypes'])
        date_ids = (1, 2, 5, 8, 9,) if types[8] == "date" else (1, 2, 5, 9,)
        for i in date_ids:
            self.adv.date_type.addItem(fields[i], userData=db_flds[i])
        self.adv.date_type.setCurrentIndex(ag.get_db_setting("DATE_TYPE", 0))

    def init_how_added(self):
        items = ("", "scan file system", "drag from file system", "import file list",
                 "drag from another instance    ", "created here")
        for it in ag.fileSource:
            self.adv.how_added.addItem(items[it.value], userData=it.value)

    def set_enable_between(self, state: bool):
        self.adv.between.setChecked(state)
        self.adv.after_btn.setEnabled(state)
        self.adv.before_btn.setEnabled(state)
        self.adv.date_after.setEnabled(state)
        self.adv.date_before.setEnabled(state)

    def set_enable_not_older(self, state: bool):
        self.adv.not_older.setChecked(state)
        self.adv.not_older_nn.setEnabled(state)
        self.adv.age_measure.setEnabled(state)

    def date_selector_clicked(self, id: int):
        if self.date_selector != -1:
            (self.set_enable_between if self.adv.date_selectors.button(self.date_selector)
             is self.adv.between else self.set_enable_not_older)(False)
        if self.date_selector == id:
            self.date_selector = -1
        else:
            self.date_selector = id
            (self.set_enable_between if self.adv.date_selectors.button(self.date_selector)
             is self.adv.between else self.set_enable_not_older)(True)

    def file_button_clicked(self, id: int):
        if self.checked_btn != -1:
            self.gen.file_buttons.button(self.checked_btn).setChecked(False)
        self.checked_btn = -1 if self.checked_btn == id else id

    def font_changed(self, font_size: str):
        cur_size = DLG_SIZE * tug.SIZE_RATIO.get(font_size, 1)
        self.ui.dlg_frame.setMinimumSize(cur_size)
        self.ui.dlg_frame.setMaximumSize(cur_size)
        self.adjustSize()

    def mouseMoveEvent(self, e: QMouseEvent):
        if e.buttons() & Qt.MouseButton.LeftButton:
            pos_ = e.globalPosition().toPoint()
            dist = pos_ - self.start_pos
            if dist.manhattanLength() < 50:
                self.move(self.pos() + dist)
                e.accept()
            self.start_pos = pos_

    def toggle_tag_check(self, state: Qt.CheckState):
        self.gen.all_btn.setEnabled(state is Qt.CheckState.Checked)
        self.gen.any_btn.setEnabled(state is Qt.CheckState.Checked)

    def is_single_folder(self) -> bool:
        return self.single_folder

    def open_clicked(self, st: bool):
        self.adv.open_edit.setEnabled(st)

    def rating_clicked(self, st: bool):
        self.adv.rating_edit.setEnabled(st)

    def done_clicked(self):
        ag.signals.filter_setup_closed.emit()
        self.close()

    def apply_clicked(self):
        ag.save_db_settings(FILTER_FILE_ID=0)
        ag.signals.user_signal.emit("filter_changed")

    def get_file_list(self):
        self.store_temp()
        self.checks['open_check'] = self.adv.open_sel.isChecked()
        self.checks['open_op'] = self.adv.open_cond.currentIndex()
        self.checks['open_val'] = self.adv.open_edit.text()
        self.checks['rating_check'] = self.adv.rating_sel.isChecked()
        self.checks['rating_op'] = self.adv.rating_cond.currentIndex()
        self.checks['rating_val'] = self.adv.rating_edit.text()
        return db_ut.filter_files(self.checks)

    def store_temp(self):
        def calc_not_older():
            nn = int(self.adv.not_older_nn.text())
            c_date = QDateTime.currentDateTime()
            return {
                "minutes": lambda x: c_date.addSecs(x * 60),
                "hours": lambda x: c_date.addSecs(x * 3600),
                "days": lambda x: c_date.addDays(x),
                "weeks": lambda x: c_date.addDays(x * 7),
                "months": lambda x: c_date.addMonths(x),
                "years": lambda x: c_date.addYears(x),
            }[self.adv.age_measure.currentText()](-nn).toSecsSinceEpoch()

        def store_date_conditions():
            """
            store after, before, date_after, date_before checks items
            """
            if self.adv.not_older.isChecked():
                self.checks['after'] = True
                self.checks['before'] = False
                self.checks['date_after'] = calc_not_older()
                return
            if self.adv.between.isChecked():
                after = QDateTime.fromString(self.adv.date_after.text(), DATE_FMT)
                if after:
                    self.checks['after'] = True
                    self.checks['date_after'] = after.toSecsSinceEpoch()
                before = QDateTime.fromString(self.adv.date_before.text(), DATE_FMT)
                if before:
                    self.checks['before'] = True
                    self.checks['date_before'] = before.toSecsSinceEpoch()

        self.checks = {
            'dir': self.gen.selected_dir.isChecked(),
            'sub_dir': self.gen.subDirs.isChecked(),
            'no_dir': self.gen.no_folder.isChecked(),
            'add_method': self.adv.add_method.isChecked(),
            'tag': self.gen.selected_tag.isChecked(),
            'ext': self.gen.selected_ext.isChecked(),
            'author': self.gen.selected_author.isChecked(),
            'date_field': self.adv.date_type.currentData(Qt.ItemDataRole.UserRole),
            'note_date': self.adv.note_date_type.currentText(),
            'after': False,
            'before': False,
        }

        store_date_conditions()

        if self.checks['add_method']:
            self.checks['how_added'] = self.adv.how_added.currentData(Qt.ItemDataRole.UserRole)

        db_ut.clear_temp()
        self.store_dir_files()
        if self.checks['tag']:
            self.store_tag_files()
        if self.checks['ext']:
            self.store_ext_ids()
        if self.checks['author']:
            self.store_author_ids()
        self.store_note_tied_files()

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
        if self.gen.all_btn.isChecked():
            tag_files = db_ut.get_tag_files(tag_ids[0])   # tag_files: set
            for id in tag_ids[1:]:
                tag_files &= db_ut.get_tag_files(id)
                if not tag_files:
                    self.checks['tag'] = False
                    return
        else:                        # self.gen.any_btn.isChecked()
            tag_files = set()
            for id in tag_ids:
                tag_files |= db_ut.get_tag_files(id)
        db_ut.save_to_temp('file_tag', ((file,) for file in tag_files))

    def store_note_tied_files(self):
        if self.adv.without_notes.isChecked():
            db_ut.save_to_temp('note_files', db_ut.files_without_notes())
            self.checks['notes_checked'] = True
            return
        self.checks['notes_checked'] = (
            self.checks['date_field'] == "note_date" and
            (self.checks['after'] or self.checks['before'])
        )
        if not self.checks['notes_checked']:
            return
        db_ut.save_to_temp('note_files', db_ut.get_note_date_files(self.checks))

    def store_ext_ids(self):
        ext_list = ag.ext_list.get_selected_ids()
        if not ext_list:   # if any extension is not selected
            self.checks['ext'] = False
            return
        db_ut.save_to_temp('ext', ((ext_id,) for ext_id in ext_list))

    def store_author_ids(self):
        authors = ag.author_list.get_selected_ids()
        if not authors:    # if any author is not selected
            self.checks['author'] = False
            return
        db_ut.save_to_temp('author', ((auth_id,) for auth_id in authors))

    def set_dir_list(self):
        indexes = ag.dir_list.selectedIndexes()
        dirs = []
        for idx in indexes:
            dirs.append(f"[{idx.data(Qt.ItemDataRole.DisplayRole)}]")
        dirs.sort(key=str.lower)
        self.gen.dir_list.setPlainText(', '.join(dirs))

    def dir_selection_changed(self):
        self.set_dir_list()
        if ag.mode is ag.appMode.FILTER and self.gen.selected_dir.isChecked():
            self.apply_clicked()

    def set_tag_list(self, tags: list[str]):
        self.gen.tag_list.setPlainText(', '.join([f"[{tag}]" for tag in tags]))

    def tag_selection_changed(self, tags: list[str]):
        self.set_tag_list(tags)
        if ag.mode is ag.appMode.FILTER and self.gen.selected_tag.isChecked():
            self.apply_clicked()

    def set_ext_list(self, exts: list[str]):
        self.gen.ext_list.setPlainText(', '.join([f"[{ext}]" for ext in exts]))

    def ext_selection_changed(self, exts: list[str]):
        self.set_ext_list(exts)
        if ag.mode is ag.appMode.FILTER and self.gen.selected_ext.isChecked():
            self.apply_clicked()

    def set_author_list(self, authors: list[str]):
        self.gen.author_list.setPlainText(
            ', '.join([f"[{author}]" for author in authors]))

    def author_selection_changed(self, authors: list[str]):
        self.set_author_list(authors)
        if ag.mode is ag.appMode.FILTER and self.gen.selected_author.isChecked():
            self.apply_clicked()

    def save_filter_settings(self):
        settings = {
            "DIR_CHECK": self.gen.selected_dir.isChecked(),
            "SUB_DIR_CHECK": self.gen.subDirs.isChecked(),
            "NO_FOLDER": self.gen.no_folder.isChecked(),
            "USE_ADD_METHOD": self.adv.add_method.isChecked(),
            "TAG_CHECK": self.gen.selected_tag.isChecked(),
            "IS_ALL": self.gen.all_btn.isChecked(),
            "HOW_ADDED": self.adv.how_added.currentIndex(),
            "EXT_CHECK": self.gen.selected_ext.isChecked(),
            "AUTHOR_CHECK": self.gen.selected_author.isChecked(),
            "OPEN_CHECK": self.adv.open_sel.isChecked(),
            "OPEN_OP": self.adv.open_cond.currentIndex(),
            "OPEN_VAL": self.adv.open_edit.text(),
            "RATING_CHECK": self.adv.rating_sel.isChecked(),
            "RATING_OP": self.adv.rating_cond.currentIndex(),
            "RATING_VAL": self.adv.rating_edit.text(),
            "DATE_TYPE": self.adv.date_type.currentIndex(),
            "NOTE_DATE_TYPE": self.adv.note_date_type.currentIndex(),
            "NOT_OLDER": self.adv.not_older.isChecked(),
            "NOT_OLDER_NN": self.adv.not_older_nn.text(),
            "AGE_MEASURE": self.adv.age_measure.currentIndex(),
            "BETWEEN": self.adv.between.isChecked(),
            "DATE_AFTER": self.adv.date_after.text(),
            "DATE_BEFORE": self.adv.date_before.text(),
            "WITHOUT_NOTES": self.adv.without_notes.isChecked(),
        }
        ag.save_db_settings(**settings)

    def restore_filter_settings(self):
        self.gen.selected_dir.setChecked(ag.get_db_setting("DIR_CHECK", False))
        if self.gen.selected_dir.isChecked():
            self.checked_btn = self.gen.file_buttons.id(self.gen.selected_dir)
        self.gen.subDirs.setChecked(ag.get_db_setting("SUB_DIR_CHECK", False))
        self.gen.no_folder.setChecked(ag.get_db_setting("NO_FOLDER", False))
        if self.gen.no_folder.isChecked():
            self.checked_btn = self.gen.file_buttons.id(self.gen.no_folder)
        self.adv.add_method.setChecked(ag.get_db_setting("USE_ADD_METHOD", False))
        self.gen.selected_tag.setChecked(ag.get_db_setting("TAG_CHECK", False))
        is_all = ag.get_db_setting("IS_ALL", False)
        self.gen.all_btn.setChecked(is_all)
        self.gen.any_btn.setChecked(not is_all)
        self.adv.how_added.setCurrentIndex(ag.get_db_setting("HOW_ADDED", 0))
        self.gen.selected_ext.setChecked(ag.get_db_setting("EXT_CHECK", False))
        self.gen.selected_author.setChecked(ag.get_db_setting("AUTHOR_CHECK", False))
        self.adv.open_sel.setChecked(ag.get_db_setting("OPEN_CHECK", False))
        self.adv.open_cond.setCurrentIndex(ag.get_db_setting("OPEN_OP", 0))
        self.adv.open_edit.setText(str(ag.get_db_setting("OPEN_VAL", "0")))
        self.adv.rating_sel.setChecked(ag.get_db_setting("RATING_CHECK", False))
        self.adv.rating_cond.setCurrentIndex(ag.get_db_setting("RATING_OP", 0))
        self.adv.rating_edit.setText(str(ag.get_db_setting("RATING_VAL", "0")))
        self.adv.without_notes.setChecked(ag.get_db_setting("WITHOUT_NOTES", False))
        self.adv.date_type.setCurrentIndex(ag.get_db_setting("DATE_TYPE", 0))
        self.adv.note_date_type.setCurrentIndex(ag.get_db_setting("NOTE_DATE_TYPE", 0))

        if ag.get_db_setting("BETWEEN", False):
            self.date_selector_clicked(self.adv.date_selectors.id(self.adv.between))
        cur_date = QDateTime.currentDateTime().toString(DATE_FMT)
        self.adv.date_after.setText(ag.get_db_setting("DATE_AFTER", cur_date))
        self.adv.date_before.setText(ag.get_db_setting("DATE_BEFORE", cur_date))

        if ag.get_db_setting("NOT_OLDER", False):
            self.date_selector_clicked(self.adv.date_selectors.id(self.adv.not_older))
        self.adv.not_older_nn.setText(ag.get_db_setting("NOT_OLDER_NN", "1"))
        self.adv.age_measure.setCurrentIndex(ag.get_db_setting("AGE_MEASURE", -1))

        self.set_tag_list(ag.tag_list.get_selected())
        self.set_ext_list(ag.ext_list.get_selected())
        self.set_author_list(ag.author_list.get_selected())
