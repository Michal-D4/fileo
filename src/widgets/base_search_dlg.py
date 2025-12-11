# from loguru import logger
import re
from PyQt6.QtWidgets import QWidget, QLineEdit, QHBoxLayout, QToolButton, QFrame

from .. import tug

class baseSearch(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.file_id = 0

        self.setup_base()
        self.rex_opt.clicked.connect(self.regex_state_changed)

    def restore_state(self, state: tuple):
        name, rex, case, self.word_checked = state
        self.srch_pattern.setText(name)
        self.srch_pattern.selectAll()
        self.rex_opt.setChecked(rex)
        self.case_opt.setChecked(case)
        self.word_opt.setChecked(self.word_checked)
        self.word_opt.setEnabled(not rex)

    def setup_base(self):
        self.srchFrame = QFrame()
        self.srchFrame.setObjectName('srchFrame')

        layout_srch = QHBoxLayout(self.srchFrame)
        layout_srch.setContentsMargins(0, 0, 0, 0)
        layout_srch.setSpacing(18)

        left_layout = QHBoxLayout()
        left_layout.setContentsMargins(0,0,0,0)
        left_layout.setSpacing(4)

        self.srch_pattern = QLineEdit()
        self.srch_pattern.setObjectName('searchLine')
        self.srch_pattern.setPlaceholderText('Input file name or its part.')
        self.srch_pattern.setToolTip('Enter - start search; Esc - cancel.')
        left_layout.addWidget(self.srch_pattern)

        self.rex_opt = QToolButton()
        self.rex_opt.setAutoRaise(True)
        self.rex_opt.setCheckable(True)
        self.rex_opt.setIcon(tug.get_icon('regex'))
        self.rex_opt.setToolTip('Regular Expression')
        left_layout.addWidget(self.rex_opt)

        self.case_opt = QToolButton()
        self.case_opt.setAutoRaise(True)
        self.case_opt.setCheckable(True)
        self.case_opt.setIcon(tug.get_icon('match_case'))
        self.case_opt.setToolTip('Match Case')
        left_layout.addWidget(self.case_opt)

        self.word_opt = QToolButton()
        self.word_opt.setAutoRaise(True)
        self.word_opt.setCheckable(True)
        self.word_opt.setIcon(tug.get_icon('match_word'))
        self.word_opt.setToolTip('Match Whole Word')
        self.word_opt.clicked.connect(self.word_state_changed)
        left_layout.addWidget(self.word_opt)
        layout_srch.addLayout(left_layout)

    def regex_state_changed(self, state: bool):
        self.word_opt.setEnabled(not state)
        if state:
            self.word_opt.setChecked(False)
        else:
            self.word_opt.setChecked(self.word_checked)

    def word_state_changed(self, state: bool):
        self.word_checked = state

    def search_text(self) -> str:
        return self.srch_pattern.text()

    def srch_params(self) -> dict:
        return {
            'txt': self.srch_pattern.text(),
            'rex': self.rex_opt.isChecked(),
            'case': self.case_opt.isChecked(),
            'whole_word': self.word_opt.isChecked()
        }

    def srch_prepare(self):
        srch = self.srch_pattern.text()
        whole_word = self.word_opt.isChecked()
        if self.rex_opt.isChecked() or whole_word:
            p = fr'\b{srch}\b' if whole_word else srch    # re - match whole word
            rex = re.compile(p) if self.case_opt.isChecked() else re.compile(p, re.IGNORECASE)
            return lambda x: rex.search(x)
        elif self.case_opt.isChecked():
            return lambda x: srch in x
        else:
            q = srch.lower()
            return lambda x: q in x.lower()
