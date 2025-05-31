from PyQt6.QtCore import Qt, QSize, QPoint
from PyQt6.QtGui import QPixmap, QKeySequence, QShortcut, QMouseEvent
from PyQt6.QtWidgets import QWidget, QStyle

from .ui_about import Ui_aboutForm
from ..core import app_globals as ag
from .. import tug


class AboutDialog(QWidget, Ui_aboutForm):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.start_pos = QPoint()

        self.ico.setPixmap(tug.get_icon('ico_app').pixmap(24, 24))
        self.set_title()
        self.app_info.setText(f'Fileo v.{ag.app_version()} - yet another file keeper')

        self.git_repo.setOpenExternalLinks(True)
        self.git_repo.setTextInteractionFlags(
            Qt.TextInteractionFlag.LinksAccessibleByMouse
        )
        link = 'https://github.com/Michal-D4/fileo'
        style = tug.get_dyn_qss('link_style')
        self.git_repo.setText(
            f"{style}GitHub repository: <a href='{link}'>{link}</a>"
        )

        f11 = QShortcut(QKeySequence(Qt.Key.Key_F11), self)
        f11.activated.connect(self.get_py_db_versions)
        esc = QShortcut(QKeySequence(Qt.Key.Key_Escape), self)
        esc.activated.connect(self.close)

        self.ok_btn.clicked.connect(self.close)
        self.ok_btn.setShortcut(QKeySequence(Qt.Key.Key_Return))

        self.mouseMoveEvent = self.move_self

    def move_self(self, e: QMouseEvent):
        if e.buttons() == Qt.MouseButton.LeftButton:
            pos_ = e.globalPosition().toPoint()
            dist = pos_ - self.start_pos
            if dist.manhattanLength() < 50:
                self.move(self.pos() + dist)
                e.accept()
            self.start_pos = pos_


    def get_info_icon(self) -> QPixmap:
        ico = QStyle.standardIcon(
            self.style(),
            QStyle.StandardPixmap.SP_MessageBoxInformation
        )
        return ico.pixmap(QSize(32, 32))

    def get_py_db_versions(self):
        import platform
        import sys

        py_ver = platform.python_version()
        if ag.db.conn:
            db_ver = ag.db.conn.execute('PRAGMA user_version').fetchone()[0]
        else:
            db_ver = ''

        mode = 'frozen' if getattr(sys, 'frozen', False) else 'packaged'

        self.set_title((py_ver, db_ver, mode))

    def set_title(self, ver: tuple=None):
        if ver:
            self.ttl_label.setText(f'About Fileo, Python {ver[0]}, DB user v.{ver[1]}, {ver[2]}')
        else:
            self.ttl_label.setText('About Fileo')

    def close(self) -> bool:
        ag.about_dialog = None
        return super().close()
