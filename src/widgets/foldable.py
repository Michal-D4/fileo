from typing import List

from loguru import logger

from PyQt6.QtWidgets import QWidget

from ..core import app_globals as ag
from .ui_foldable import Ui_foldable
from .. import tug

class Foldable(QWidget):
    """
    The Foldable widget is designed for the left sidebar
    to implement expanded/collapsed views on it.
    """
    qss_decorator: List

    def __init__(self, parent: QWidget=None) -> None:
        QWidget.__init__(self, parent)

        self.ui = Ui_foldable()
        self.ui.setupUi(self)
        self.ui.decorator.setStyleSheet(self.qss_decorator[0])

        self._toggle_icon()

        self.ui.toFold.clicked.connect(self.on_click)
        ag.buttons.append((self.ui.toFold, "down", "right"))

    def set_decoration(self, to_show: bool) -> None:
        """
        widget can be decorated with a horizontal line on top.
        This line is used to change the height of the widget by dragging the line
        """
        self.ui.decorator.setVisible(to_show)

    def on_click(self):
        """
        on_click header toggles the expanded/collapsed state of the widget
        """
        self.toggle_collapse()

        ag.signals_.collapseSignal.emit(self, self.ui.toFold.isChecked())

    def set_hovering(self, hover: bool):
        if hover:
            qss = ''.join(self.qss_decorator)
        else:
            qss = self.qss_decorator[0]

        self.ui.decorator.setStyleSheet(qss)

    @classmethod
    def set_decorator_qss(cls, qss: List):
        cls.qss_decorator = qss

    def _toggle_icon(self):
        self.ui.toFold.setIcon(
           tug.get_icon("right") if self.ui.toFold.isChecked()
           else tug.get_icon("down")
        )

    def toggle_collapse(self):
        is_collapsed = self.ui.toFold.isChecked()
        self.ui.inner.setVisible(not is_collapsed)
        self._toggle_icon()

    def set_title(self, title: str):
        """
        set header title
        """
        self.ui.toFold.setText(title.upper())

    def add_widget(self, w: QWidget) -> None:
        """
        add QWidget to the QFrame fold_head
        """
        self.ui.headerLayout.addWidget(w)

    def get_inner_widget(self) -> QWidget:
        return self.ui.inner
