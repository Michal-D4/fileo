# from loguru import logger
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtWidgets import (QWidget, QLineEdit,
    QHBoxLayout, QToolButton, QFrame, QSizePolicy,
    QMessageBox,
)

from ..core  import app_globals as ag
from .. import tug


class srchFiles(QWidget):
    """
    Dialog to search for a file in the database by its name,
    there may be multiple files
    """
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.file_id = 0

        self.setup_ui()
        self.srch_pattern.returnPressed.connect(self.search_files)

        escape = QShortcut(QKeySequence(Qt.Key.Key_Escape), self)
        escape.activated.connect(self.close)

    def setup_ui(self):
        self.srch_pattern = QLineEdit()
        self.srch_pattern.setObjectName('searchLine')
        self.srch_pattern.setPlaceholderText('Input file name or its part.')
        self.srch_pattern.setToolTip('Enter - start search; Esc - cancel.')

        self.case = QToolButton()
        self.case.setAutoRaise(True)
        self.case.setCheckable(True)
        self.case.setIcon(tug.get_icon('match_case'))
        self.case.setToolTip('Match Case')

        self.word = QToolButton()
        self.word.setAutoRaise(True)
        self.word.setCheckable(True)
        self.word.setIcon(tug.get_icon('match_word'))
        self.word.setToolTip('Match Whole Word')

        name, case, word = ag.get_setting('SEARCH_FILE', ('',0,0))
        self.srch_pattern.setText(name)
        self.srch_pattern.selectAll()
        self.case.setChecked(case)
        self.word.setChecked(word)

        self.srchFrame = QFrame()
        self.srchFrame.setObjectName('srchFrame')

        layout = QHBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget(self.srch_pattern)
        layout.addWidget(self.case)
        layout.addWidget(self.word)
        self.srchFrame.setLayout(layout)
        self.resize(320, 36)

        m_layout = QHBoxLayout(self)
        m_layout.setContentsMargins(0,0,0,0)
        m_layout.addWidget(self.srchFrame)
        si_policy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setSizePolicy(si_policy)

    def search_files(self):
        # close if found, otherwise show message and leave open
        name, case, word = (
            self.srch_pattern.text(),
            self.case.isChecked(),
            self.word.isChecked()
        )
        if not name:
            self.search_err_msg('Please enter file name')
            return

        ag.save_settings(SEARCH_FILE=(name, case, word))
        ag.signals_.user_signal.emit(
            f'find_files_by_name\\{name}0{int(case)}{int(word)}'
        )
        self.close()

    def search_err_msg(self, msg):
        dlg = QMessageBox(ag.app)
        dlg.setWindowTitle('File not found')
        dlg.setText(msg)
        dlg.setStandardButtons(QMessageBox.StandardButton.Close)
        dlg.setIcon(QMessageBox.Icon.Warning)
        dlg.exec()
        self.srch_pattern.setFocus()
