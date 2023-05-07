from loguru import logger

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtWidgets import (QWidget, QLineEdit,
    QHBoxLayout, QToolButton, QFrame, QSizePolicy,
    QMessageBox,
)

from ..core  import app_globals as ag, db_ut, icons


class findFile(QWidget):
    """
    Dialog to search for a file in the database by its name,
    there may be multiple files
    """
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.file_id = 0

        self.setStyleSheet(' '.join(ag.dyn_qss['searchFrame']))
        self.setup_ui()
        self.srch_pattern.editingFinished.connect(self.search_files)

        escape = QShortcut(QKeySequence(Qt.Key.Key_Escape), self)
        escape.activated.connect(self.close)

    def setup_ui(self):
        self.srch_pattern = QLineEdit()
        self.srch_pattern.setObjectName('searchLine')
        self.srch_pattern.setToolTip('Find')

        self.case = QToolButton()
        self.case.setAutoRaise(True)
        self.case.setCheckable(True)
        self.case.setIcon(icons.get_other_icon('match_case'))
        self.case.setToolTip('Match Case')

        self.word = QToolButton()
        self.word.setAutoRaise(True)
        self.word.setCheckable(True)
        self.word.setIcon(icons.get_other_icon('match_word'))
        self.word.setToolTip('Exact match')

        self.frame = QFrame()
        self.frame.setObjectName('frame')

        layout = QHBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget(self.srch_pattern)
        layout.addWidget(self.case)
        layout.addWidget(self.word)
        self.frame.setLayout(layout)
        self.resize(320, 32)

        m_layout = QHBoxLayout(self)
        m_layout.setContentsMargins(0,0,0,0)
        m_layout.addWidget(self.frame)
        si_policy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setSizePolicy(si_policy)

    def search_files(self):
        # close if found, otherwise show message and leave open
        name, case, word = (
            self.srch_pattern.text(),
            self.case.isChecked(),
            self.word.isChecked()
        )
        if db_ut.exists_file_with_name(name, case, word):
            ag.signals_.user_action_signal.emit(
                f'find_files_by_name/{name},{int(case)},{int(word)}'
            )
            self.close()
        else:
            dlg = QMessageBox(ag.app)
            dlg.setWindowTitle(f'File not found"')
            dlg.setText(f'File "{name}" not found')
            dlg.setStandardButtons(QMessageBox.StandardButton.Close)
            dlg.setIcon(QMessageBox.Icon.Warning)
            dlg.exec()
