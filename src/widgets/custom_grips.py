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
from loguru import logger

from PyQt6.QtCore import QRect, QSize, Qt, QPoint
from PyQt6.QtGui import QCursor, QMouseEvent
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QSizeGrip, QWidget

from ..core import app_globals as ag

GT = 10        # Grip Thickness
G2 = GT*2
MG = GT//2

class CustomGrip(QWidget):
    def __init__(self, parent: QWidget, edge: Qt.Edge):
        super().__init__(parent)
        self.parent: QWidget = parent
        self.edge: Qt.Edge = edge
        self.wi = Grips()

        self.resize_parent = {
            Qt.Edge.TopEdge: self.set_top,
            Qt.Edge.BottomEdge: self.set_bottom,
            Qt.Edge.LeftEdge: self.set_left,
            Qt.Edge.RightEdge: self.set_right
        }[edge]()  # move_top, move_bottom, move_left, move_right

    def set_top(self):
        self.wi.top(self)
        self.setGeometry(0, 0, self.parent.width(), GT)
        self.setMaximumHeight(GT)

        QSizeGrip(self.wi.top_left)
        QSizeGrip(self.wi.top_right)

        def move_top(pos: QPoint):
            rect: QRect = self.parent.geometry()
            rect.setTop(pos.y())
            self.parent.setGeometry(rect)

        return move_top

    def set_bottom(self):
        self.wi.bottom(self)
        self.setGeometry(0, self.parent.height() - GT, self.parent.width(), GT)
        self.setMaximumHeight(GT)

        QSizeGrip(self.wi.bottom_left)
        QSizeGrip(self.wi.bottom_right)

        def move_bottom(pos: QPoint):
            height = pos.y() - self.parent.y()
            self.parent.resize(self.parent.width(), height)

        return move_bottom

    def set_left(self):
        self.wi.left(self)
        self.setGeometry(0, GT, GT, self.parent.height() - G2)
        self.setMaximumWidth(GT)

        def move_left(pos: QPoint):
            rect = self.parent.geometry()
            rect.setLeft(pos.x())
            self.parent.setGeometry(rect)

        return move_left

    def set_right(self):
        self.wi.right(self)
        self.setGeometry(self.parent.width() - GT, GT, GT, self.parent.height() - G2)
        self.setMaximumWidth(GT)

        def move_right(pos: QPoint):
            width = pos.x() - self.parent.x()
            self.parent.resize(width, self.parent.height())

        return move_right

    def mouseMoveEvent(self, e: QMouseEvent) -> None:
        self.resize_parent(e.globalPosition().toPoint())
        return super().mouseMoveEvent(e)

    def resizeEvent(self, e):
        if self.edge & (Qt.Edge.TopEdge | Qt.Edge.BottomEdge):
            self.wi.grip.setGeometry(
                0, 0, self.parent.width(), GT)
        elif self.edge & (Qt.Edge.LeftEdge | Qt.Edge.RightEdge):
            self.wi.grip.setGeometry(
                0, 0, GT, self.parent.height() - G2)


class Grips(object):
    ssq = "background-color: rgba(222, 222, 222, 1%)"
    def top(self, Form):
        if not Form.objectName():
            Form.setObjectName("Form")
        self.grip = QFrame(Form)
        self.grip.setObjectName("container_top")
        self.grip.setMinimumSize(QSize(0, GT))
        self.grip.setMaximumSize(QSize(16777215, GT))
        self.grip.setFrameShape(QFrame.Shape.NoFrame)
        self.grip.setFrameShadow(QFrame.Shadow.Raised)
        self.top_layout = QHBoxLayout(self.grip)
        self.top_layout.setSpacing(0)
        self.top_layout.setObjectName("top_layout")
        self.top_layout.setContentsMargins(0, 0, 0, 0)
        self.top_left = QFrame(self.grip)
        self.top_left.setObjectName("top_left")
        self.top_left.setMinimumSize(QSize(GT, GT))
        self.top_left.setMaximumSize(QSize(GT, GT))
        self.top_left.setCursor(QCursor(Qt.CursorShape.SizeFDiagCursor))
        self.top_left.setStyleSheet(self.ssq)
        self.top_left.setFrameShape(QFrame.Shape.NoFrame)
        self.top_left.setFrameShadow(QFrame.Shadow.Raised)
        self.top_layout.addWidget(self.top_left)
        self.top = QFrame(self.grip)
        self.top.setObjectName("top")
        self.top.setCursor(QCursor(Qt.CursorShape.SizeVerCursor))
        self.top.setStyleSheet(self.ssq)
        self.top.setFrameShape(QFrame.Shape.NoFrame)
        self.top.setFrameShadow(QFrame.Shadow.Raised)
        self.top_layout.addWidget(self.top)
        self.top_right = QFrame(self.grip)
        self.top_right.setObjectName("top_right")
        self.top_right.setMinimumSize(QSize(GT, GT))
        self.top_right.setMaximumSize(QSize(GT, GT))
        self.top_right.setCursor(QCursor(Qt.CursorShape.SizeBDiagCursor))
        self.top_right.setStyleSheet(self.ssq)
        self.top_right.setFrameShape(QFrame.Shape.NoFrame)
        self.top_right.setFrameShadow(QFrame.Shadow.Raised)
        self.top_layout.addWidget(self.top_right)

    def bottom(self, Form):
        if not Form.objectName():
            Form.setObjectName("Form")
        self.grip = QFrame(Form)
        self.grip.setObjectName("container_bottom")
        self.grip.setMinimumSize(QSize(0, GT))
        self.grip.setMaximumSize(QSize(16777215, GT))
        self.grip.setFrameShape(QFrame.Shape.NoFrame)
        self.grip.setFrameShadow(QFrame.Shadow.Raised)
        self.bottom_layout = QHBoxLayout(self.grip)
        self.bottom_layout.setSpacing(0)
        self.bottom_layout.setObjectName("bottom_layout")
        self.bottom_layout.setContentsMargins(0, 0, 0, 0)
        self.bottom_left = QFrame(self.grip)
        self.bottom_left.setObjectName("bottom_left")
        self.bottom_left.setMinimumSize(QSize(GT, GT))
        self.bottom_left.setMaximumSize(QSize(GT, GT))
        self.bottom_left.setCursor(QCursor(Qt.CursorShape.SizeBDiagCursor))
        self.bottom_left.setStyleSheet(self.ssq)
        self.bottom_left.setFrameShape(QFrame.Shape.NoFrame)
        self.bottom_left.setFrameShadow(QFrame.Shadow.Raised)
        self.bottom_layout.addWidget(self.bottom_left)
        self.bottom = QFrame(self.grip)
        self.bottom.setObjectName("bottom")
        self.bottom.setCursor(QCursor(Qt.CursorShape.SizeVerCursor))
        self.bottom.setStyleSheet(self.ssq)
        self.bottom.setFrameShape(QFrame.Shape.NoFrame)
        self.bottom.setFrameShadow(QFrame.Shadow.Raised)
        self.bottom_layout.addWidget(self.bottom)
        self.bottom_right = QFrame(self.grip)
        self.bottom_right.setObjectName("bottom_right")
        self.bottom_right.setMinimumSize(QSize(GT, GT))
        self.bottom_right.setMaximumSize(QSize(GT, GT))
        self.bottom_right.setCursor(QCursor(Qt.CursorShape.SizeFDiagCursor))
        self.bottom_right.setStyleSheet(self.ssq)
        self.bottom_right.setFrameShape(QFrame.Shape.NoFrame)
        self.bottom_right.setFrameShadow(QFrame.Shadow.Raised)
        self.bottom_layout.addWidget(self.bottom_right)

    def left(self, Form):
        if not Form.objectName():
            Form.setObjectName("Form")
        self.grip = QFrame(Form)
        self.grip.setObjectName("left")
        self.grip.setMinimumSize(QSize(GT, 0))
        self.grip.setCursor(QCursor(Qt.CursorShape.SizeHorCursor))
        self.grip.setStyleSheet(self.ssq)
        self.grip.setFrameShape(QFrame.Shape.NoFrame)
        self.grip.setFrameShadow(QFrame.Shadow.Raised)

    def right(self, Form):
        if not Form.objectName():
            Form.setObjectName("Form")
        self.grip = QFrame(Form)
        self.grip.setObjectName("right")
        self.grip.setMinimumSize(QSize(GT, 0))
        self.grip.setCursor(QCursor(Qt.CursorShape.SizeHorCursor))
        self.grip.setStyleSheet(self.ssq)
        self.grip.setFrameShape(QFrame.Shape.NoFrame)
        self.grip.setFrameShadow(QFrame.Shadow.Raised)
