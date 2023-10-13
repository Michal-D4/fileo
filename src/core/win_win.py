from loguru import logger
import qtawesome as qta

from PyQt6.QtCore import Qt, QEvent, QPoint
from PyQt6.QtGui import QMouseEvent

from . import utils, app_globals as ag, icons
from ..widgets.custom_grips import CustomGrip

def activate(pid):
    from pywinauto import Application

    running_app = Application().connect(process=int(pid))
    running_app.top_window().set_focus()

def win_icons():
    icons.toolbar_icons["minimize"] = (
        qta.icon('mdi.window-minimize', color=ag.qss_params["$topBarColor"]),
    )

    icons.toolbar_icons["maximize"] = (
        qta.icon('mdi.window-maximize', color=ag.qss_params["$topBarColor"]),
        qta.icon('mdi.window-restore', color=ag.qss_params["$topBarColor"]),
    )

    icons.toolbar_icons["close"] = (
        qta.icon('mdi.window-close', color=ag.qss_params["$topBarColor"],
            color_active=ag.qss_params["$ToolButtonActiveColor"]),
    )


def setup_ui(self):
    self.setWindowFlags(
        Qt.WindowType.FramelessWindowHint |
        Qt.WindowType.WindowMinMaxButtonsHint
    )
    self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    self.ui.close.clicked.connect(self.close_app)
    self.ui.minimize.clicked.connect(self.minimize)

    # CUSTOM GRIPS
    self.grips = {}
    self.grips['left_grip'] = CustomGrip(self, Qt.Edge.LeftEdge)
    self.grips['right_grip'] = CustomGrip(self, Qt.Edge.RightEdge)
    self.grips['top_grip'] = CustomGrip(self, Qt.Edge.TopEdge)
    self.grips['bottom_grip'] = CustomGrip(self, Qt.Edge.BottomEdge)

    def maximize_restore():
        self.window_maximized = not self.window_maximized
        self.ui.maximize.setIcon(self.icons["maximize"][self.window_maximized])
        if self.window_maximized:
            self.ui.appMargins.setContentsMargins(0, 0, 0, 0)
            [grip.hide() for grip in self.grips.values()]
            self.showMaximized()
        else:
            self.ui.appMargins.setContentsMargins(ag.GT, ag.GT, ag.GT, ag.GT)
            [grip.show() for grip in self.grips.values()]
            self.showNormal()

    self.ui.maximize.clicked.connect(maximize_restore)

    def move_window(e: QMouseEvent):
        if self.window_maximized:
            maximize_restore()
            return
        if e.buttons() == Qt.MouseButton.LeftButton:
            pos_ = e.globalPosition().toPoint()
            logger.info(f'pos_: ({pos_.x()}, {pos_.y()}), self.start_move: ({self.start_move.x(), self.start_move.y()})')
            if (pos_ - self.start_move).manhattanLength() < ag.MOVE_THRESHOLD:
                logger.info(f'self.pos: ({self.pos().x()}, {self.pos().y()})')
                win_pos = QPoint(self.x(), self.y())
                tmp = win_pos + pos_ - self.start_move
                logger.info(f'new  pos: ({tmp.x()}, {tmp.y()})')
                self.move(win_pos + pos_ - self.start_move)
            self.start_move = pos_
            e.accept()

    self.ui.topBar.mouseMoveEvent = move_window
    self.ui.status.mouseMoveEvent = move_window
    self.ui.toolBar.mouseMoveEvent = move_window
    self.container.ui.navi_header.mouseMoveEvent = move_window

    is_maximized = int(utils.get_app_setting("maximizedWindow", False))
    if is_maximized:
        maximize_restore()

    def double_click_maximize_restore(e: QMouseEvent):
        if e.type() == QEvent.Type.MouseButtonDblClick:
            maximize_restore()

    self.ui.topBar.mouseDoubleClickEvent = double_click_maximize_restore
    # for grip in self.grips.values():
    #     ag.signals_.initiate_grids.connect(grip.update_grips)
