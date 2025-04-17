import os
from pathlib import Path

from PyQt6.QtCore import pyqtSlot, QSize, QPoint, Qt
from PyQt6.QtGui import QPixmap, QMouseEvent, QKeySequence
from PyQt6.QtWidgets import QStyle, QWidget

from ..core import app_globals as ag, db_ut
from .ui_dup import Ui_DlgDup
from .. import tug

class dlgDup(QWidget, Ui_DlgDup):
    def __init__(self, report: dict[list], parent=None) -> None:
        super().__init__(parent)
        self.setupUi(self)
        self.start_pos = QPoint()

        self.setFixedSize(self.size())
        self.report = report
        self.ico.setPixmap(self.get_dlg_icon())
        self.is_user_request = False

        self.close_btn.clicked.connect(self.close)
        self.close_btn.setShortcut(QKeySequence(Qt.Key.Key_Escape))
        self.del_btn.clicked.connect(self.delete_duplicates)
        self.show_btn.clicked.connect(self.show_duplicates)
        self.mouseMoveEvent = self.move_self

    def move_self(self, e: QMouseEvent):
        if e.buttons() == Qt.MouseButton.LeftButton:
            pos_ = e.globalPosition().toPoint()
            dist = pos_ - self.start_pos
            if dist.manhattanLength() < 50:
                self.move(self.pos() + dist)
                e.accept()
            self.start_pos = pos_

    def asked_by_user(self, user_request: bool):
        self.is_user_request = user_request
        # logger.info(f'{user_request=}')
        if self.is_user_request:
            self.checkBox.hide()
            self.save_report()

    @pyqtSlot()
    def delete_duplicates(self):
        for hash_, file_dups in self.report.items():
            # delete all except first (with the shortest path)
            for path, file_id in file_dups[1:]:
                try:
                    os.remove(str(path))
                except FileNotFoundError:
                    pass
                finally:   # delete from DB independent on os.remove result
                    db_ut.delete_file(file_id)
        self.close()

    def save_report(self) -> Path:
        path = self.get_report_path()
        self.save_dup_report(path)
        return path

    def get_report_path(self) -> Path:
        pp = Path('~/fileo/report').expanduser()
        return Path(
            tug.get_app_setting('DEFAULT_REPORT_PATH', str(pp))
        ) / f"duplicate_files.{ag.app.ui.db_name.text()}.log"

    @pyqtSlot()
    def show_duplicates(self):
        path = self.get_report_path() if self.is_user_request else self.save_report()
        ag.signals_.user_signal.emit(f"Open file by path\\{str(path)}")

    def save_dup_report(self, path: Path):
        with open(path, "w") as out:
            out.write(f'DB path: {ag.db.path}\n')
            for rr in self.report.values():
                out.write(f"{'-='*20}-\n")
                for p, _ in rr:
                    out.write(f"   * {str(p)}\n")

    def get_dlg_icon(self) -> QPixmap:
        ico = QStyle.standardIcon(
            self.style(),
            QStyle.StandardPixmap.SP_MessageBoxWarning
        )
        return ico.pixmap(QSize(32, 32))

    def close(self) -> bool:
        if not self.is_user_request:
            tug.save_app_setting(CHECK_DUPLICATES = int(not self.checkBox.isChecked()))
        return super().close()
