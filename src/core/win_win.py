from loguru import logger

from PyQt6.QtCore import Qt, QEvent, QPoint
from PyQt6.QtGui import QMouseEvent, QPixmap, QIcon
from PyQt6.QtWidgets import QApplication

from ..widgets import custom_grips as cg
from src import tug

MOVE_THRESHOLD = 50

def activate(pid):
    from pywinauto import Application

    running_app = Application().connect(process=int(pid))
    running_app.top_window().set_focus()

def win_icons():
    keys = {
        'minimize': ('minimize',),
        'maximize': ('maximize', 'restore'),
        'close': ('close', 'close_active'),
    }
    tug.set_icons(keys)

def set_app_icon(app: QApplication):
    try:
        from ctypes import windll  # to show icon on the taskbar - Windows only
        myappid = '.'.join((tug.MAKER, tug.APP_NAME))
        windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except ImportError:
        pass

    pict = QPixmap()
    if pict.load(tug.qss_params['$ico_app']):
        ico = QIcon()
        ico.addPixmap(pict)
        app.setWindowIcon(ico)

def setup_ui(self):
    self.start_move = QPoint()

    self.setWindowFlags(
        Qt.WindowType.FramelessWindowHint |
        Qt.WindowType.WindowMinMaxButtonsHint
    )
    self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    self.ui.close.clicked.connect(self.close_app)
    self.ui.minimize.clicked.connect(self.minimize)

    # CUSTOM GRIPS
    self.grips = {}
    self.grips['left_grip'] = cg.CustomGrip(self, Qt.Edge.LeftEdge)
    self.grips['right_grip'] = cg.CustomGrip(self, Qt.Edge.RightEdge)
    self.grips['top_grip'] = cg.CustomGrip(self, Qt.Edge.TopEdge)
    self.grips['bottom_grip'] = cg.CustomGrip(self, Qt.Edge.BottomEdge)

    def maximize_restore():
        self.window_maximized = not self.window_maximized
        self.ui.maximize.setIcon(tug.get_icon("maximize", self.window_maximized))
        if self.window_maximized:
            self.ui.appMargins.setContentsMargins(0, 0, 0, 0)
            [grip.hide() for grip in self.grips.values()]
            self.showMaximized()
        else:
            self.ui.appMargins.setContentsMargins(cg.GT, cg.GT, cg.GT, cg.GT)
            [grip.show() for grip in self.grips.values()]
            self.showNormal()

    self.ui.maximize.clicked.connect(maximize_restore)

    def move_window(e: QMouseEvent):
        if self.window_maximized:
            maximize_restore()
            return
        if e.buttons() == Qt.MouseButton.LeftButton:
            pos_ = e.globalPosition().toPoint()
            if (pos_ - self.start_move).manhattanLength() < MOVE_THRESHOLD:
                self.move(self.pos() + pos_ - self.start_move)
            self.start_move = pos_
            e.accept()

    self.ui.topBar.mouseMoveEvent = move_window
    self.ui.status.mouseMoveEvent = move_window
    self.ui.toolBar.mouseMoveEvent = move_window
    self.container.ui.navi_header.mouseMoveEvent = move_window

    is_maximized = int(tug.get_app_setting("maximizedWindow", False))
    if is_maximized:
        maximize_restore()

    def double_click_maximize_restore(e: QMouseEvent):
        if e.type() == QEvent.Type.MouseButtonDblClick:
            maximize_restore()

    self.ui.topBar.mouseDoubleClickEvent = double_click_maximize_restore

def update_grips(self):
    self.grips['left_grip'].setGeometry(
        0, cg.GT, cg.GT, self.height()-2*cg.GT)
    self.grips['right_grip'].setGeometry(
        self.width() - cg.GT, cg.GT, cg.GT, self.height()-2*cg.GT)
    self.grips['top_grip'].setGeometry(
        0, 0, self.width(), cg.GT)
    self.grips['bottom_grip'].setGeometry(
        0, self.height() - cg.GT, self.width(), cg.GT)
