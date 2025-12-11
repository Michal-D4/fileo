# from loguru import logger
from PyQt6.QtWidgets import QHBoxLayout, QSizePolicy

from ..core  import app_globals as ag
from .base_search_dlg import baseSearch
from .cust_msgbox import show_message_box


class srchFiles(baseSearch):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.file_id = 0

        self.setup_ui()
        self.srch_pattern.returnPressed.connect(self.search_files)

        self.restore_state(ag.get_db_setting('RE_SEARCH_FILE', ('',0,0,0)))

        ag.popups['srchFiles'] = self

    def setup_ui(self):
        m_layout = QHBoxLayout(self)
        m_layout.setContentsMargins(0,0,0,0)

        self.resize(320, 36)

        m_layout.addWidget(self.srchFrame)
        si_policy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setSizePolicy(si_policy)

    def search_files(self):
        # close if found, otherwise show message and leave open
        name = self.srch_pattern.text()

        if not name:
            show_message_box("File not found", "Please enter file name or its part")
            return

        ag.save_db_settings(RE_SEARCH_FILE=(
            name, self.rex_opt.isChecked(),self.case_opt.isChecked(), self.word_checked))
        ag.signals.user_signal.emit('find_files_by_name')
        self.close()

    def closeEvent(self, a0):
        ag.popups.pop('srchFiles')
        return super().closeEvent(a0)
