from PyQt6.QtWidgets import QWidget, QLineEdit

from ..core import app_globals as ag
from .ui_foldable import Ui_foldable
from .. import tug

class Foldable(QWidget):
    """
    The Foldable widget is designed for the left sidebar
    to implement expanded/collapsed views on it.
    """
    def __init__(self, parent: QWidget=None) -> None:
        QWidget.__init__(self, parent)

        self.ui = Ui_foldable()
        self.ui.setupUi(self)
        self.ui.decorator.setStyleSheet(tug.get_dyn_qss('decorator_p'))

        self._toggle_icon()

        self.ui.toFold.clicked.connect(self.on_click)
        ag.buttons[self.ui.toFold.objectName()] = (self.ui.toFold, "down", "right")

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

        ag.signals.collapseSignal.emit(self, self.ui.toFold.isChecked())

    def set_hovering(self, hover: bool):
        if hover:
            qss = tug.get_dyn_qss('decorator_p,decorator_a')
        else:
            qss = tug.get_dyn_qss('decorator_p')

        self.ui.decorator.setStyleSheet(qss)

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

        editor = QLineEdit(self)
        editor.editingFinished.connect(finish_edit)

        editor_setup()

        editor.show()
        editor.setFocus()
