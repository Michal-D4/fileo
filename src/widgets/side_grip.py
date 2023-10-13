from loguru import logger
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtWidgets import  QWidget

class SideGrip(QWidget):
    def __init__(self, parent, edge: Qt.Edge):
        self.edge = edge.name
        logger.info(f'{self.edge}')
        super().__init__(parent)
        if edge == Qt.Edge.LeftEdge:
            self.setCursor(Qt.CursorShape.SizeHorCursor)
            self.resizeFunc = self.resizeLeft
        elif edge == Qt.Edge.TopEdge:
            self.setCursor(Qt.CursorShape.SizeVerCursor)
            self.resizeFunc = self.resizeTop
        elif edge == Qt.Edge.RightEdge:
            self.setCursor(Qt.CursorShape.SizeHorCursor)
            self.resizeFunc = self.resizeRight
        else:  # edge == Qt.Edge.BottomEdge
            self.setCursor(Qt.CursorShape.SizeVerCursor)
            self.resizeFunc = self.resizeBottom
        self.mousePos = QPoint()

    def resizeLeft(self, delta):
        window = self.window()
        width = max(window.minimumWidth(), window.width() - delta.x())
        geo = window.geometry()
        geo.setLeft(geo.right() - width)
        window.setGeometry(geo)

    def resizeTop(self, delta):
        window = self.window()
        height = max(window.minimumHeight(), window.height() - delta.y())
        geo = window.geometry()
        geo.setTop(geo.bottom() - height)
        window.setGeometry(geo)

    def resizeRight(self, delta):
        window = self.window()
        width = max(window.minimumWidth(), window.width() + delta.x())
        window.resize(width, window.height())

    def resizeBottom(self, delta):
        window = self.window()
        height = max(window.minimumHeight(), window.height() + delta.y())
        window.resize(window.width(), height)

    def mousePressEvent(self, event: QMouseEvent):
        logger.info(f'{self.edge}, {self.mousePos=}, {event.pos()=}')
        if event.button() == Qt.MouseButton.LeftButton:
            self.mousePos = event.pos()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.mousePos is not None:
            delta = event.pos() - self.mousePos
            self.resizeFunc(delta)

    def mouseReleaseEvent(self, event: QMouseEvent):
        logger.info(f'{self.edge}, {self.mousePos=}, {event.pos()=}')
        self.mousePos = QPoint()
