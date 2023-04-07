from loguru import logger

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (QDialog, QLabel, QSizePolicy,
    QHBoxLayout, QVBoxLayout, QDialogButtonBox,
)

from core import icons

class AboutDialog(QDialog):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle('About Fileo')
        self.buttonBox = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Close
        )
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        v_layout = QVBoxLayout(self)
        v_layout.setSpacing(16)

        h_layout = QHBoxLayout(self)
        h_layout.setSpacing(24)

        ico = QLabel(self)
        size_policy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        ico.setSizePolicy(size_policy)
        ico.setMinimumSize(QSize(32, 32))
        ico.setPixmap(icons.get_other_icon('info'))
        h_layout.addWidget(ico)

        sub = QLabel(self)
        sub.setText('Fileo - yet another file keeper')
        font = QFont()
        font.setPointSize(16)
        sub.setFont(font)

        self.git_repo = QLabel(self)
        self.git_repo.setText('GitHub repository: https://github.com/Michal-D4/fileo')
        self.git_repo.setOpenExternalLinks(True)
        self.git_repo.setTextInteractionFlags(Qt.TextInteractionFlag.LinksAccessibleByMouse)
        # ('https://github.com/Michal-D4/fileo')
        font = QFont()
        font.setPointSize(12)
        self.git_repo.setFont(font)

        v_layout2 = QVBoxLayout()
        v_layout2.setSpacing(24)

        v_layout2.addWidget(sub, Qt.AlignmentFlag.AlignCenter)
        v_layout2.addWidget(self.git_repo, Qt.AlignmentFlag.AlignCenter)

        h_layout.addLayout(v_layout2)

        v_layout.addLayout(h_layout)
        v_layout.addWidget(self.buttonBox)
