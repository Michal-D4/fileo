from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (QDialog, QLabel, QSizePolicy,
    QHBoxLayout, QVBoxLayout, QDialogButtonBox, QStyle,
)


class AboutDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle('About Fileo')
        self.buttonBox = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Close
        )
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

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

        from ..main import app_version

        app_info = QLabel(self)
        app_info.setText(f'Fileo v.{app_version()} - yet another file keeper')
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
        v_layout.addWidget(self.buttonBox)
        self.setModal(True)

    def get_info_icon(self) -> QPixmap:
        ico = QStyle.standardIcon(
            self.style(),
            QStyle.StandardPixmap.SP_MessageBoxInformation
        )
        return ico.pixmap(QSize(32, 32))
