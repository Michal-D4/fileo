# ///////////////////////////////////////////////////////////////
# https://github.com/Wanderson-Magalhaes/Modern_GUI_PyDracula_PySide6_or_PyQt6.git
#
# BY: WANDERSON M.PIMENTA
# PROJECT MADE WITH: Qt Designer and PySide6
# V: 1.0.0
#
# This project can be used freely for all uses, as long as they maintain the
# respective credits only in the Python scripts, any information in the visual
# interface (GUI) can be modified without any implication.
#
# There are limitations on Qt licenses if you want to use your products
# commercially, I recommend reading them on the official website:
# https://doc.qt.io/qtforpython/licenses.html
#
# ///////////////////////////////////////////////////////////////

from PyQt6.QtCore import QRect, QSize, Qt
from PyQt6.QtGui import QCursor
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QSizeGrip, QWidget

from ..core import app_globals as ag


class CustomGrip(QWidget):
    def __init__(self, parent, position, disable_color = False):

        # SETUP UI
        QWidget.__init__(self)
        self.parent = parent
        self.setParent(parent)
        self.wi = Widgets()

        # SHOW TOP GRIP
        if position == Qt.Edge.TopEdge:
            self.wi.top(self)
            self.setGeometry(0, 0, self.parent.width(), ag.GT)
            self.setMaximumHeight(ag.GT)

            # GRIPS
            top_left = QSizeGrip(self.wi.top_left)
            top_right = QSizeGrip(self.wi.top_right)

            # RESIZE TOP
            def resize_top(event):
                delta = event.position()
                height = max(self.parent.minimumHeight(), self.parent.height() - delta.y())
                geo = self.parent.geometry()
                geo.setTop(int(geo.bottom() - height))
                self.parent.setGeometry(geo)
                event.accept()
            self.wi.top.mouseMoveEvent = resize_top

        # SHOW BOTTOM GRIP
        elif position == Qt.Edge.BottomEdge:
            self.wi.bottom(self)
            self.setGeometry(0, self.parent.height() - ag.GT, self.parent.width(), ag.GT)
            self.setMaximumHeight(ag.GT)

            # GRIPS
            self.bottom_left = QSizeGrip(self.wi.bottom_left)
            self.bottom_right = QSizeGrip(self.wi.bottom_right)

            # RESIZE BOTTOM
            def resize_bottom(event):
                delta = event.position()
                height = int(max(self.parent.minimumHeight(), self.parent.height() + delta.y()))
                self.parent.resize(self.parent.width(), height)
                event.accept()
            self.wi.bottom.mouseMoveEvent = resize_bottom

        # SHOW LEFT GRIP
        elif position == Qt.Edge.LeftEdge:
            self.wi.left(self)
            self.setGeometry(0, ag.GT, ag.GT, self.parent.height())
            self.setMaximumWidth(ag.GT)

            # RESIZE LEFT
            def resize_left(event):
                delta = event.position()
                width = max(self.parent.minimumWidth(), self.parent.width() - delta.x())
                geo = self.parent.geometry()
                geo.setLeft(int(geo.right() - width))
                self.parent.setGeometry(geo)
                event.accept()
            self.wi.leftgrip.mouseMoveEvent = resize_left

        # RESIZE RIGHT
        elif position == Qt.Edge.RightEdge:
            self.wi.right(self)
            self.setGeometry(self.parent.width() - ag.GT, ag.GT, ag.GT, self.parent.height())
            self.setMaximumWidth(ag.GT)

            def resize_right(event):
                delta = event.position()
                width = int(max(self.parent.minimumWidth(), self.parent.width() + delta.x()))
                self.parent.resize(width, self.parent.height())
                event.accept()
            self.wi.rightgrip.mouseMoveEvent = resize_right

    def resizeEvent(self, event):
        if hasattr(self.wi, 'container_top'):
            self.wi.container_top.setGeometry(0, 0, self.width(), ag.GT)

        elif hasattr(self.wi, 'container_bottom'):
            self.wi.container_bottom.setGeometry(0, 0, self.width(), ag.GT)

        elif hasattr(self.wi, 'leftgrip'):
            self.wi.leftgrip.setGeometry(0, 0, ag.GT, self.height() - ag.GT)

        elif hasattr(self.wi, 'rightgrip'):
            self.wi.rightgrip.setGeometry(0, 0, ag.GT, self.height() - ag.GT)


class Widgets(object):
    def top(self, Form):
        if not Form.objectName():
            Form.setObjectName("Form")
        self.container_top = QFrame(Form)
        self.container_top.setObjectName("container_top")
        self.container_top.setGeometry(QRect(0, 0, 500, ag.GT))
        self.container_top.setMinimumSize(QSize(0, ag.GT))
        self.container_top.setMaximumSize(QSize(16777215, ag.GT))
        self.container_top.setFrameShape(QFrame.Shape.NoFrame)
        self.container_top.setFrameShadow(QFrame.Shadow.Raised)
        self.top_layout = QHBoxLayout(self.container_top)
        self.top_layout.setSpacing(0)
        self.top_layout.setObjectName("top_layout")
        self.top_layout.setContentsMargins(0, 0, 0, 0)
        self.top_left = QFrame(self.container_top)
        self.top_left.setObjectName("top_left")
        self.top_left.setMinimumSize(QSize(ag.GT, ag.GT))
        self.top_left.setMaximumSize(QSize(ag.GT, ag.GT))
        self.top_left.setCursor(QCursor(Qt.CursorShape.SizeFDiagCursor))
        self.top_left.setStyleSheet("background-color: rgba(222, 222, 222, 1%)")
        self.top_left.setFrameShape(QFrame.Shape.NoFrame)
        self.top_left.setFrameShadow(QFrame.Shadow.Raised)
        self.top_layout.addWidget(self.top_left)
        self.top = QFrame(self.container_top)
        self.top.setObjectName("top")
        self.top.setCursor(QCursor(Qt.CursorShape.SizeVerCursor))
        self.top.setStyleSheet("background-color: rgba(222, 222, 222, 1%)")
        self.top.setFrameShape(QFrame.Shape.NoFrame)
        self.top.setFrameShadow(QFrame.Shadow.Raised)
        self.top_layout.addWidget(self.top)
        self.top_right = QFrame(self.container_top)
        self.top_right.setObjectName("top_right")
        self.top_right.setMinimumSize(QSize(ag.GT, ag.GT))
        self.top_right.setMaximumSize(QSize(ag.GT, ag.GT))
        self.top_right.setCursor(QCursor(Qt.CursorShape.SizeBDiagCursor))
        self.top_right.setStyleSheet("background-color: rgba(222, 222, 222, 1%)")
        self.top_right.setFrameShape(QFrame.Shape.NoFrame)
        self.top_right.setFrameShadow(QFrame.Shadow.Raised)
        self.top_layout.addWidget(self.top_right)

    def bottom(self, Form):
        if not Form.objectName():
            Form.setObjectName("Form")
        self.container_bottom = QFrame(Form)
        self.container_bottom.setObjectName("container_bottom")
        self.container_bottom.setGeometry(QRect(0, 0, 500, ag.GT))
        self.container_bottom.setMinimumSize(QSize(0, ag.GT))
        self.container_bottom.setMaximumSize(QSize(16777215, ag.GT))
        self.container_bottom.setFrameShape(QFrame.Shape.NoFrame)
        self.container_bottom.setFrameShadow(QFrame.Shadow.Raised)
        self.bottom_layout = QHBoxLayout(self.container_bottom)
        self.bottom_layout.setSpacing(0)
        self.bottom_layout.setObjectName("bottom_layout")
        self.bottom_layout.setContentsMargins(0, 0, 0, 0)
        self.bottom_left = QFrame(self.container_bottom)
        self.bottom_left.setObjectName("bottom_left")
        self.bottom_left.setMinimumSize(QSize(ag.GT, ag.GT))
        self.bottom_left.setMaximumSize(QSize(ag.GT, ag.GT))
        self.bottom_left.setCursor(QCursor(Qt.CursorShape.SizeBDiagCursor))
        self.bottom_left.setStyleSheet("background-color: rgba(222, 222, 222, 1%)")
        self.bottom_left.setFrameShape(QFrame.Shape.NoFrame)
        self.bottom_left.setFrameShadow(QFrame.Shadow.Raised)
        self.bottom_layout.addWidget(self.bottom_left)
        self.bottom = QFrame(self.container_bottom)
        self.bottom.setObjectName("bottom")
        self.bottom.setCursor(QCursor(Qt.CursorShape.SizeVerCursor))
        self.bottom.setStyleSheet("background-color: rgba(222, 222, 222, 1%)")
        self.bottom.setFrameShape(QFrame.Shape.NoFrame)
        self.bottom.setFrameShadow(QFrame.Shadow.Raised)
        self.bottom_layout.addWidget(self.bottom)
        self.bottom_right = QFrame(self.container_bottom)
        self.bottom_right.setObjectName("bottom_right")
        self.bottom_right.setMinimumSize(QSize(ag.GT, ag.GT))
        self.bottom_right.setMaximumSize(QSize(ag.GT, ag.GT))
        self.bottom_right.setCursor(QCursor(Qt.CursorShape.SizeFDiagCursor))
        self.bottom_right.setStyleSheet("background-color: rgba(222, 222, 222, 1%)")
        self.bottom_right.setFrameShape(QFrame.Shape.NoFrame)
        self.bottom_right.setFrameShadow(QFrame.Shadow.Raised)
        self.bottom_layout.addWidget(self.bottom_right)

    def left(self, Form):
        if not Form.objectName():
            Form.setObjectName("Form")
        self.leftgrip = QFrame(Form)
        self.leftgrip.setObjectName("left")
        self.leftgrip.setGeometry(QRect(0, ag.GT, ag.GT, 480))
        self.leftgrip.setMinimumSize(QSize(ag.GT, 0))
        self.leftgrip.setCursor(QCursor(Qt.CursorShape.SizeHorCursor))
        self.leftgrip.setStyleSheet("background-color: rgba(222, 222, 222, 1%)")
        self.leftgrip.setFrameShape(QFrame.Shape.NoFrame)
        self.leftgrip.setFrameShadow(QFrame.Shadow.Raised)

    def right(self, Form):
        if not Form.objectName():
            Form.setObjectName("Form")
        Form.resize(500, 500)
        self.rightgrip = QFrame(Form)
        self.rightgrip.setObjectName("right")
        self.rightgrip.setGeometry(QRect(0, 0, ag.GT, 500))
        self.rightgrip.setMinimumSize(QSize(ag.GT, 0))
        self.rightgrip.setCursor(QCursor(Qt.CursorShape.SizeHorCursor))
        self.rightgrip.setStyleSheet("background-color: rgba(222, 222, 222, 1%)")
        self.rightgrip.setFrameShape(QFrame.Shape.NoFrame)
        self.rightgrip.setFrameShadow(QFrame.Shadow.Raised)
