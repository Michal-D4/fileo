from pathlib import Path

from PyQt6.QtCore import Qt, pyqtSlot, QPoint
from PyQt6.QtGui import QMouseEvent, QKeySequence
from PyQt6.QtWidgets import QWidget, QFileDialog

from .ui_scan_disk import Ui_scanDisk

from ..core import app_globals as ag
from .. import tug


class diskScanner(QWidget):
    def __init__(self, parent = None) -> None:
        super().__init__(parent)

        self.ui = Ui_scanDisk()
        self.ui.setupUi(self)
        self.ui.ico.setPixmap(tug.get_icon('ico_app').pixmap(24, 24))

        self.ui.open_btn.setIcon(tug.get_icon("folder_open"))

        self.ui.open_btn.clicked.connect(self.get_root_path)

        self.ui.btnCancel.clicked.connect(self.close)
        self.ui.btnCancel.setShortcut(QKeySequence(Qt.Key.Key_Escape))
        self.ui.btnGo.clicked.connect(self.go)
        self.ui.btnGo.setShortcut(QKeySequence(Qt.Key.Key_Return))
        self.start_pos = QPoint()
        self.mouseMoveEvent = self.move_self

        self.set_exts()

    @pyqtSlot()
    def go(self):
        # start scanning
        root = Path(self.ui.root_dir.text()).absolute()
        if not root.exists():
            self.ui.root_dir.setPlaceholderText(
                f'path "{str(root)}" does not exist'
            )
            return
        if not root.is_dir():
            root = root.parent

        exts = [s.strip() for s in self.ui.extensions.text().split(',')]
        if self.ui.no_ext.isChecked():
            exts.append('')

        ag.signals_.start_disk_scanning.emit(str(root), exts)
        self.close()

    def set_exts(self):
        self.ui.extensions.setText(", ".join(ag.ext_list.get_selected()))

    @pyqtSlot()
    def get_root_path(self):
        sel_path = QFileDialog.getExistingDirectory(
            self, "Select start search path", str(Path.home()))
        if sel_path:
            self.ui.root_dir.setText(sel_path)

    def move_self(self, e: QMouseEvent):
        if e.buttons() == Qt.MouseButton.LeftButton:
            pos_ = e.globalPosition().toPoint()
            dist = pos_ - self.start_pos
            if dist.manhattanLength() < 50:
                self.move(self.pos() + dist)
                e.accept()
            self.start_pos = pos_

    def close(self) -> bool:
        ag.take_files = None
        return super().close()
