# from loguru import logger
from PyQt6.QtWidgets import QHBoxLayout, QToolButton, QFrame, QSizePolicy

from ..core  import app_globals as ag
from .. import tug
from .base_search_dlg import baseSearch
from .cust_msgbox import show_message_box


class srchInNotes(baseSearch):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.file_id = 0

        self.setup_ui()
        self.srch_pattern.returnPressed.connect(self.search_files)

        self.restore_state(ag.get_db_setting('SEARCH_BY_NOTE', ('',0,0,0)))

        ag.popups['srchInNotes'] = self

    def setup_ui(self):
        m_layout = QHBoxLayout(self)
        m_layout.setContentsMargins(0,0,0,0)

        layout_srch = self.srchFrame.layout()

        self.btns = QFrame(parent=self.srchFrame)
        layout_r = QHBoxLayout(self.btns)
        layout_r.setContentsMargins(0, 0, 0, 0)
        layout_r.setSpacing(4)

        self.prev_btn = QToolButton(parent=self.btns)
        self.prev_btn.setToolTip('Prev match')
        self.prev_btn.setIcon(tug.get_icon('prev_match'))
        self.prev_btn.setEnabled(False)
        layout_r.addWidget(self.prev_btn)
        self.next_btn = QToolButton(parent=self.btns)
        self.next_btn.setToolTip('Next match')
        self.next_btn.setIcon(tug.get_icon('next_match'))
        self.next_btn.setEnabled(False)
        layout_r.addWidget(self.next_btn)
        layout_srch.addWidget(self.btns)

        self.resize(380, 36)

        m_layout.addWidget(self.srchFrame)
        si_policy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setSizePolicy(si_policy)

    def search_files(self):
        # close if found, otherwise show message and leave open
        txt = self.srch_pattern.text()

        if not txt:
            show_message_box("File not found", "Please enter text to search")
            return

        ag.save_db_settings(SEARCH_BY_NOTE=(
            txt, self.rex_opt.isChecked(),self.case_opt.isChecked(), self.word_checked))
        ag.signals.user_signal.emit('srch_files_by_note')

    def closeEvent(self, a0):
        ag.popups.pop('srchInNotes')
        return super().closeEvent(a0)
