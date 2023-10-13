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


class CustomGrip(QWidget):
    def __init__(self, parent, edge: Qt.Edge):
        super().__init__(parent)
        self.parent = parent
        self.edge = edge
        self.wi = Widgets()
        self.start_move = QPoint()

        self.resize_func = {
            Qt.Edge.TopEdge: self.set_top,
            Qt.Edge.BottomEdge: self.set_bottom,
            Qt.Edge.LeftEdge: self.set_left,
            Qt.Edge.RightEdge: self.set_right
        }[edge]()

    def set_top(self):
        self.wi.top(self)
        self.setGeometry(0, 0, self.parent.width(), ag.GT)
        self.setMaximumHeight(ag.GT)

        top_left = QSizeGrip(self.wi.top_left)
        top_right = QSizeGrip(self.wi.top_right)

        def resize_top(delta: QPoint):
            if 0 < delta.manhattanLength() < ag.MOVE_THRESHOLD:
                height = max(self.parent.minimumHeight(), self.parent.height() - delta.y())
                geo: QRect = self.parent.geometry()
                logger.info(f'{delta.y()=}; {self.parent.height()=}, {height=}')
                geo.setTop(int(geo.bottom() - height))
                self.parent.setGeometry(geo)

        return resize_top

    def set_bottom(self):
        self.wi.bottom(self)
        self.setGeometry(0, self.parent.height() - ag.GT, self.parent.width(), ag.GT)
        self.setMaximumHeight(ag.GT)

        self.bottom_left = QSizeGrip(self.wi.bottom_left)
        self.bottom_right = QSizeGrip(self.wi.bottom_right)

        def resize_bottom(delta: QPoint):
            if 0 < delta.manhattanLength() < ag.MOVE_THRESHOLD:
                height = int(max(self.parent.minimumHeight(), self.parent.height() + delta.y()))
                logger.info(f'{delta.y()=}; {self.parent.height()=}, {height=}')
                self.parent.resize(self.parent.width(), height)

        return resize_bottom

    def set_left(self):
        self.wi.left(self)
        self.setGeometry(0, ag.GT, ag.GT, self.parent.height() - 2*ag.GT)
        self.setMaximumWidth(ag.GT)

        def resize_left(delta: QPoint):
            if 0 < delta.manhattanLength() < ag.MOVE_THRESHOLD:
                width = max(self.parent.minimumWidth(), self.parent.width() - delta.x())
                geo = self.parent.geometry()
                logger.info(f'{delta.x()=}; {self.parent.width()=}, {width=}')
                geo.setLeft(int(geo.right() - width))
                self.parent.setGeometry(geo)

        return resize_left

    def set_right(self):
        self.wi.right(self)
        self.setGeometry(self.parent.width() - ag.GT, ag.GT, ag.GT, self.parent.height() - 2*ag.GT)
        self.setMaximumWidth(ag.GT)

        def resize_right(delta: QPoint):
            if 0 < delta.manhattanLength() < ag.MOVE_THRESHOLD:
                width = int(max(self.parent.minimumWidth(), self.parent.width() + delta.x()))
                logger.info(f'{delta.x()=}; {self.parent.width()=}, {width=}')
                self.parent.resize(width, self.parent.height())

        return resize_right

    def mouseMoveEvent(self, e: QMouseEvent):
        pos = e.pos()
        self.resize_func(pos - self.start_move)
        self.start_move = pos

    def mousePressEvent(self, event):
        logger.info(f'{self.edge}, {self.start_move=}, {event.pos()=}')
        rect=self.geometry()
        logger.info(f'{rect.left(), rect.top(), rect.width(), rect.height()}')
        if event.button() == Qt.MouseButton.LeftButton:
            self.start_move = event.pos()

    def mouseReleaseEvent(self, event):
        logger.info(f'{self.edge}, {self.start_move=}, {event.pos()=}')
        rect=self.geometry()
        logger.info(f'{rect.left(), rect.top(), rect.width(), rect.height()}')
        self.start_move = QPoint()
        # self.update_grip()   # it isn't current grip which size has been changed

    def update_grip(self):
        '''
        the method should be called to the perpendicular instances of grip:
        LeftEdge, RightEdge <-> TopEdge, BottomEdge
        i.e. it should be called from win_win.py
        '''
        logger.info(f'{self.edge.name}: {self.width()=}, {self.height()=}')
        if self.edge == Qt.Edge.LeftEdge:
            self.setGeometry(0, ag.GT, ag.GT, self.height()-2*ag.GT)
        elif self.edge == Qt.Edge.RightEdge:
            self.setGeometry(
                self.width() - ag.GT, ag.GT, ag.GT, self.height()-2*ag.GT)
        elif self.edge == Qt.Edge.TopEdge:
            self.setGeometry(0, 0, self.width(), ag.GT)
        else:
            self.setGeometry(0, self.height() - ag.GT, self.width(), ag.GT)
        logger.info(f"{self.edge.name}: {self.geometry()}")


class Widgets(object):
    ssq = "background-color: rgba(222, 222, 222, 50%)"
    def top(self, Form):
        if not Form.objectName():
            Form.setObjectName("Form")
        self.container_top = QFrame(Form)
        self.container_top.setObjectName("container_top")
        # self.container_top.setGeometry(QRect(0, 0, 500, ag.GT))
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
        self.top_left.setStyleSheet(self.ssq)
        self.top_left.setFrameShape(QFrame.Shape.NoFrame)
        self.top_left.setFrameShadow(QFrame.Shadow.Raised)
        self.top_layout.addWidget(self.top_left)
        self.top_ = QFrame(self.container_top)
        self.top_.setObjectName("top")
        self.top_.setCursor(QCursor(Qt.CursorShape.SizeVerCursor))
        self.top_.setStyleSheet(self.ssq)
        self.top_.setFrameShape(QFrame.Shape.NoFrame)
        self.top_.setFrameShadow(QFrame.Shadow.Raised)
        self.top_layout.addWidget(self.top_)
        self.top_right = QFrame(self.container_top)
        self.top_right.setObjectName("top_right")
        self.top_right.setMinimumSize(QSize(ag.GT, ag.GT))
        self.top_right.setMaximumSize(QSize(ag.GT, ag.GT))
        self.top_right.setCursor(QCursor(Qt.CursorShape.SizeBDiagCursor))
        self.top_right.setStyleSheet(self.ssq)
        self.top_right.setFrameShape(QFrame.Shape.NoFrame)
        self.top_right.setFrameShadow(QFrame.Shadow.Raised)
        self.top_layout.addWidget(self.top_right)

    def bottom(self, Form):
        if not Form.objectName():
            Form.setObjectName("Form")
        self.container_bottom = QFrame(Form)
        self.container_bottom.setObjectName("container_bottom")
        # self.container_bottom.setGeometry(QRect(0, 0, 500, ag.GT))
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
        self.bottom_left.setStyleSheet(self.ssq)
        self.bottom_left.setFrameShape(QFrame.Shape.NoFrame)
        self.bottom_left.setFrameShadow(QFrame.Shadow.Raised)
        self.bottom_layout.addWidget(self.bottom_left)
        self.bottom_ = QFrame(self.container_bottom)
        self.bottom_.setObjectName("bottom")
        self.bottom_.setCursor(QCursor(Qt.CursorShape.SizeVerCursor))
        self.bottom_.setStyleSheet(self.ssq)
        self.bottom_.setFrameShape(QFrame.Shape.NoFrame)
        self.bottom_.setFrameShadow(QFrame.Shadow.Raised)
        self.bottom_layout.addWidget(self.bottom_)
        self.bottom_right = QFrame(self.container_bottom)
        self.bottom_right.setObjectName("bottom_right")
        self.bottom_right.setMinimumSize(QSize(ag.GT, ag.GT))
        self.bottom_right.setMaximumSize(QSize(ag.GT, ag.GT))
        self.bottom_right.setCursor(QCursor(Qt.CursorShape.SizeFDiagCursor))
        self.bottom_right.setStyleSheet(self.ssq)
        self.bottom_right.setFrameShape(QFrame.Shape.NoFrame)
        self.bottom_right.setFrameShadow(QFrame.Shadow.Raised)
        self.bottom_layout.addWidget(self.bottom_right)

    def left(self, Form):
        if not Form.objectName():
            Form.setObjectName("Form")
        self.leftgrip = QFrame(Form)
        self.leftgrip.setObjectName("left")
        # self.leftgrip.setGeometry(QRect(0, ag.GT, ag.GT, 480))
        self.leftgrip.setMinimumSize(QSize(ag.GT, 0))
        self.leftgrip.setCursor(QCursor(Qt.CursorShape.SizeHorCursor))
        self.leftgrip.setStyleSheet(self.ssq)
        self.leftgrip.setFrameShape(QFrame.Shape.NoFrame)
        self.leftgrip.setFrameShadow(QFrame.Shadow.Raised)

    def right(self, Form):
        if not Form.objectName():
            Form.setObjectName("Form")
        Form.resize(500, 500)
        self.rightgrip = QFrame(Form)
        self.rightgrip.setObjectName("right")
        # self.rightgrip.setGeometry(QRect(0, 0, ag.GT, 500))
        self.rightgrip.setMinimumSize(QSize(ag.GT, 0))
        self.rightgrip.setCursor(QCursor(Qt.CursorShape.SizeHorCursor))
        self.rightgrip.setStyleSheet(self.ssq)
        self.rightgrip.setFrameShape(QFrame.Shape.NoFrame)
        self.rightgrip.setFrameShadow(QFrame.Shadow.Raised)
