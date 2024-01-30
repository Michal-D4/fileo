from loguru import logger
import sys

from PyQt6.QtCore import Qt, QEvent, QPoint
from PyQt6.QtGui import QMouseEvent, QPixmap, QIcon
from PyQt6.QtWidgets import QApplication

from ..widgets import custom_grips as cg
from src import tug

MOVE_THRESHOLD = 50

if sys.platform.startswith("win"):
    def activate(pid):
        from pywinauto import Application

        running_app = Application().connect(process=int(pid))
        running_app.top_window().set_focus()
elif sys.platform.startswith("linux"):
    import subprocess
    from . import utils
    def activate(pid):
        try:
            temp = subprocess.Popen(
                ['wmctrl', '-p', '-l'], stdout = subprocess.PIPE
            )
            rr = temp.communicate()
            pp = str(rr[0]).split(r'\n')
            p_id = get_win_id(pp, str(pid))
            if p_id:
                subprocess.Popen(
                    ['wmctrl', '-i', '-R', f'{p_id}'], stdout = subprocess.PIPE
                )
        except FileNotFoundError:
            utils.show_message_box(
                "Can't switch to existed fileo instance",
                "Please install 'wmctrl' on your system."
            )


    def get_win_id(comm: list, pid: str) -> str:
        for cc in comm:
            if pid in cc:
                p = cc.find('0x')
                return cc[p:p+10]
        return ''
else:
    raise ImportError(f"doesn't support {sys.platform} system")

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
    self._geom = None

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
        if self.isMaximized():
            self.ui.appMargins.setContentsMargins(cg.MG, cg.MG, cg.MG, cg.MG)
            [grip.show() for grip in self.grips.values()]
            self.setGeometry(self._geom)
        else:
            self._geom = self.normalGeometry()
            self.ui.appMargins.setContentsMargins(0, 0, 0, 0)
            [grip.hide() for grip in self.grips.values()]
            self.showMaximized()
        self.ui.maximize.setIcon(tug.get_icon("maximize", self.isMaximized()))

    self.ui.maximize.clicked.connect(maximize_restore)

    def move_window(e: QMouseEvent):
        if self.isMaximized():
            maximize_restore()
            return
        if e.buttons() == Qt.MouseButton.LeftButton:
            pos_ = e.globalPosition().toPoint()
            a_pos = self.pos()
            if (pos_ - self.start_move).manhattanLength() < MOVE_THRESHOLD:
                self.move(a_pos + pos_ - self.start_move)
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
        0, cg.GT, cg.GT, self.height()-cg.G2)
    self.grips['right_grip'].setGeometry(
        self.width() - cg.GT, cg.GT, cg.GT, self.height()-cg.G2)
    self.grips['top_grip'].setGeometry(
        0, 0, self.width(), cg.GT)
    self.grips['bottom_grip'].setGeometry(
        0, self.height() - cg.GT, self.width(), cg.GT)
