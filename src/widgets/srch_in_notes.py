from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtWidgets import (QWidget, QLineEdit,
    QHBoxLayout, QToolButton, QFrame, QSizePolicy,
    QMessageBox,
)

from ..core  import app_globals as ag
from .. import tug


class srchInNotes(QWidget):

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
        self.srch_pattern.setPlaceholderText('Input text to search')
        self.srch_pattern.setToolTip('Enter - start search; Esc - cancel.')

        self.rex = QToolButton()
        self.rex.setAutoRaise(True)
        self.rex.setCheckable(True)
        self.rex.setIcon(tug.get_icon('regex'))
        self.rex.setToolTip('Regular Expression')
        self.rex.clicked.connect(self.regex_state_changed)

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

        name, rex, case, word = ag.get_setting('SEARCH_BY_NOTE', ('',0,0,0))
        self.srch_pattern.setText(name)
        self.srch_pattern.selectAll()
        self.rex.setChecked(rex)
        self.case.setChecked(case)
        self.word.setChecked(word)
        self.word.setEnabled(not rex)

        self.srchFrame = QFrame()
        self.srchFrame.setObjectName('srchFrame')

        layout = QHBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget(self.srch_pattern)
        layout.addWidget(self.rex)
        layout.addWidget(self.case)
        layout.addWidget(self.word)
        self.srchFrame.setLayout(layout)
        self.resize(320, 36)

        m_layout = QHBoxLayout(self)
        m_layout.setContentsMargins(0,0,0,0)
        m_layout.addWidget(self.srchFrame)
        si_policy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setSizePolicy(si_policy)

    def regex_state_changed(self, state: bool):
        self.word.setEnabled(not state)

    def search_files(self):
        # close if found, otherwise show message and leave open
        txt, rex, case, word = (
            self.srch_pattern.text(),
            self.rex.isChecked(),
            self.case.isChecked(),
            self.word.isChecked()
        )
        if not txt:
            self.search_err_msg('Please enter text to search')
            return

        ag.save_settings(SEARCH_BY_NOTE=(txt, rex, case, word))
        ag.signals_.user_signal.emit(
            f'srch_files_by_note\\{txt},{int(rex)},{int(case)},{int(word)}'
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
