from loguru import logger

from PyQt6.QtCore import Qt, QSize, QPoint
from PyQt6.QtGui import QPixmap, QKeySequence, QShortcut
from PyQt6.QtWidgets import (QDialog, QLabel, QSizePolicy,
    QHBoxLayout, QVBoxLayout, QDialogButtonBox, QStyle,
    QSpinBox, QToolButton, QFrame
)

from ..core import app_globals as ag
from src import tug


class AboutDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.set_title()
        self.buttonBox = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Close
        )
        self.buttonBox.rejected.connect(self.close)

        v_layout = QVBoxLayout(self)
        v_layout.setContentsMargins(16, 16, 16, 16)
        v_layout.setSpacing(16)

        h_layout = QHBoxLayout()
        h_layout.setSpacing(16)

        ico = QLabel(self)
        size_policy = QSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
        )
        ico.setSizePolicy(size_policy)
        ico.setMinimumSize(QSize(40, 40))
        ico.setPixmap(self.get_info_icon())
        h_layout.addWidget(ico)

        app_info = QLabel(self)
        app_info.setText(f'Fileo v.{ag.app_version()} - yet another file keeper')
        h_layout.addWidget(app_info)

        self.git_repo = QLabel(self)
        self.git_repo.setOpenExternalLinks(True)
        self.git_repo.setTextInteractionFlags(
            Qt.TextInteractionFlag.LinksAccessibleByMouse
        )
        link = 'https://github.com/Michal-D4/fileo'
        self.git_repo.setText(
            f"GitHub repository: <a href='{link}'>{link}</a>"
        )

        v_layout.addLayout(h_layout)
        v_layout.addWidget(self.git_repo)

        if tug.config.get('test', False):
            self.set_test_box(v_layout)

        v_layout.addWidget(self.buttonBox)
        self.setModal(True)

        f11 = QShortcut(QKeySequence(Qt.Key.Key_F11), self)
        f11.activated.connect(self.get_py_db_versions)

    def set_test_box(self, layout):
        from .custom_grips import CustomGrip
        logger.info(f'{ag.app.geometry()=}')

        def click_left():
            grip: CustomGrip = ag.app.grips['left_grip']
            pos = ag.app.pos()
            logger.info(f'{pos=}, {self.incr.value()=}')
            pos.setX(pos.x() - self.incr.value())
            grip.resize_parent(pos)

        def click_right():
            grip: CustomGrip = ag.app.grips['right_grip']
            rect = ag.app.geometry()
            logger.info(f'{rect=}, {self.incr.value()=}')
            grip.resize_parent(QPoint(rect.right() + self.incr.value(), rect.y()))

        def click_up():
            grip: CustomGrip = ag.app.grips['top_grip']
            pos = ag.app.pos()
            logger.info(f'{pos=}, {self.incr.value()=}')
            pos.setY(pos.y() - self.incr.value())
            grip.resize_parent(pos)

        def click_down():
            grip: CustomGrip = ag.app.grips['bottom_grip']
            rect = ag.app.geometry()
            logger.info(f'{rect=}, {self.incr.value()=}')
            grip.resize_parent(QPoint(rect.x(), rect.bottom() + self.incr.value()))

        self.incr = QSpinBox()
        self.incr.setMinimum(-50)
        self.incr.setMaximum(50)

        self.dir_left = QToolButton()
        self.dir_left.setArrowType(Qt.ArrowType.LeftArrow)

        self.dir_right = QToolButton()
        self.dir_right.setArrowType(Qt.ArrowType.RightArrow)

        self.dir_up = QToolButton()
        self.dir_up.setArrowType(Qt.ArrowType.UpArrow)

        self.dir_down = QToolButton()
        self.dir_down.setArrowType(Qt.ArrowType.DownArrow)

        test_layout = QHBoxLayout()
        test_layout.addWidget(self.incr)
        test_layout.addStretch(1)
        test_layout.addWidget(self.dir_left)
        test_layout.addWidget(self.dir_right)
        test_layout.addWidget(self.dir_up)
        test_layout.addWidget(self.dir_down)

        frame = QFrame()
        frame.setLayout(test_layout)

        layout.addWidget(frame)

        self.dir_left.clicked.connect(click_left)
        self.dir_right.clicked.connect(click_right)
        self.dir_up.clicked.connect(click_up)
        self.dir_down.clicked.connect(click_down)

    def get_info_icon(self) -> QPixmap:
        ico = QStyle.standardIcon(
            self.style(),
            QStyle.StandardPixmap.SP_MessageBoxInformation
        )
        return ico.pixmap(QSize(32, 32))

    def get_py_db_versions(self):
        import platform
        py_ver = platform.python_version()
        if ag.db.conn:
            db_ver = ag.db.conn.execute('PRAGMA user_version').fetchone()[0]
        else:
            db_ver = ''
        self.set_title((py_ver, db_ver))

    def set_title(self, ver: tuple=None):
        if ver:
            self.setWindowTitle(f'About Fileo, Python {ver[0]}, DB user v.{ver[1]}')
        else:
            self.setWindowTitle('About Fileo')
