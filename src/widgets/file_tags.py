from ..core.compact_list import aBrowser
from ..core import app_globals as ag

class tagBrowser(aBrowser):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

    def show_in_bpowser(self):
        style = ag.dyn_qss['text_browser'][0]
        self.browser.clear()

        txt = ''.join((style, self.html_selected()))

        self.browser.setText(txt)

    def html_selected(self):
        sel = self.selected_idx
        inn = ' '.join(f"<a class={'s' if i in sel else 't'} href=#{tag}>{tag}</a> "
             for i,tag in enumerate(self.tags))
        return inn
