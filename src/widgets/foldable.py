# from loguru import logger

from PyQt6.QtCore import QEvent, Qt
from PyQt6.QtWidgets import QWidget, QLineEdit, QSizePolicy

from ..core import app_globals as ag
from .ui_foldable import Ui_foldable
from .. import tug

THRESHOLD = 9
MIN_HEIGHT = 62

class titleEdit(QLineEdit):
    def __init__(self, parent = ...):
        super().__init__(parent)
        self.installEventFilter(self)

    def eventFilter(self, watched, event):
        if event.type() == QEvent.Type.KeyRelease:
            if event.key() == Qt.Key.Key_Escape:
                self.close()
                return True
        return super().eventFilter(watched, event)

class Foldable(QWidget):
    def __init__(self, parent: QWidget=None) -> None:
        QWidget.__init__(self, parent)
        self.seq: int = -1      # -1 means not installed into container

        self.ui = Ui_foldable()
        self.ui.setupUi(self)
        s_policy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.MinimumExpanding)
        s_policy.setHorizontalStretch(0)
        s_policy.setVerticalStretch(1)
        self.setSizePolicy(s_policy)

        self.__is_hidden: bool = False
        self.is_collapsed: bool = False
        self.height_inner = 0

        self._toggle_icon()

        ag.buttons[self.ui.toFold.objectName()] = (self.ui.toFold, "down", "right")

    def on_click(self, state: bool):
        self.toggle_collapse(state)
        ag.signals.collapseSignal.emit(self.seq, state)

    def toggle_collapse(self, state: bool):
        self.is_collapsed = state
        self.ui.inner.setVisible(not state)
        self._toggle_icon()

    def height(self):
        """  0 for hidden, super().height() returns height before hidden  """
        return 0 if self.__is_hidden else super().height()

    def resizeEvent(self, a0):
        if not self.is_collapsed:
            if a0.oldSize().height() > 0:
                hh = a0.size().height()
                self.setMinimumHeight(hh)
                self.height_inner = hh - self.ui.toFold.height()
        return super().resizeEvent(a0)

    @property
    def is_hidden(self) -> bool:
        return self.__is_hidden

    @is_hidden.setter
    def is_hidden(self, state: bool):
        self.__is_hidden = state
        self.setVisible(not state)

    @property
    def seqno(self) -> int:
        return self.seq

    @seqno.setter
    def seqno(self, val: int):
        self.seq = val

    def _toggle_icon(self):
        self.ui.toFold.setIcon(tug.get_icon("right" if self.is_collapsed else "down"))

    def set_title(self, title: str):
        self.ui.toFold.setText(title.upper())

    def add_widget(self, w: QWidget) -> None:
        """  add QWidget to the QFrame fold_head  """
        self.ui.headerLayout.addWidget(w)

    def get_inner_frame(self) -> QWidget:
        return self.ui.inner

    def change_title(self, pos):
        def finish_edit():
            ttl = editor.text().lower()
            self.ui.toFold.setText(ttl.upper())
            ttls = tug.get_app_setting('FOLD_TITLES', tug.qss_params['$FoldTitles'])
            tug.save_app_setting(FOLD_TITLES=(*ttls[:-1], ttl))
            ag.signals.author_widget_title.emit(ttl)
            editor.close()

        def editor_setup():
            rect = self.ui.toFold.rect()
            rect.moveTo(
                rect.left() + rect.height(),
                rect.top() + rect.height() - 2
            )

            editor.setGeometry(rect)
            editor.setText(self.ui.toFold.text())
            editor.selectAll()

        editor = titleEdit(self)
        editor.editingFinished.connect(finish_edit)

        editor_setup()

        editor.show()
        editor.setFocus()
