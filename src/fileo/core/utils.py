from loguru import logger

from typing import Any, Optional
import importlib.resources as resources


from PyQt6.QtCore import QEvent, Qt, QSettings, QVariant
from PyQt6.QtGui import QMouseEvent, QIcon
from PyQt6.QtWidgets import QApplication

from core import app_globals as ag

__all__ = ['setup_ui', 'resize_grips',
            'get_setting', 'save_setting',
]

APP_NAME = "fileBox"
MAKER = 'miha'

settings = None


def get_setting(key: str, default: Optional[Any]=None) -> QVariant:
    global settings
    if not settings:
        settings = QSettings(MAKER, APP_NAME)
    return settings.value(key, default) or default

def save_setting(**kwargs):
    if not kwargs:
        return
    global settings
    if not settings:
        settings = QSettings(MAKER, APP_NAME)

    for key, value in kwargs.items():
        settings.setValue(key, QVariant(value))

def setup_ui(self):
    from widgets.custom_grips import CustomGrip

    # CUSTOM GRIPS
    self.grips = {}
    self.grips['left_grip'] = CustomGrip(self, Qt.Edge.LeftEdge, True)
    self.grips['right_grip'] = CustomGrip(self, Qt.Edge.RightEdge, True)
    self.grips['top_grip'] = CustomGrip(self, Qt.Edge.TopEdge, True)
    self.grips['bottom_grip'] = CustomGrip(self, Qt.Edge.BottomEdge, True)

    def maximize_restore():
        self.window_maximized = not self.window_maximized
        self.ui.maximize.setIcon(self.icons["maximize"][self.window_maximized])
        if self.window_maximized:
            self.ui.appMargins.setContentsMargins(0, 0, 0, 0)
            [grip.hide() for grip in self.grips.values()]
            self.showMaximized()
        else:
            self.ui.appMargins.setContentsMargins(10, 10, 10, 10)
            [grip.show() for grip in self.grips.values()]
            self.showNormal()

    self.ui.maximize.clicked.connect(maximize_restore)

    def move_window(e: QMouseEvent):
        if self.window_maximized:
            maximize_restore()
            return
        if e.buttons() == Qt.MouseButton.LeftButton:
            pos_ = e.globalPosition().toPoint()
            if (pos_ - self.start_move_pos).manhattanLength() < 100:
                self.move(self.pos() + pos_ - self.start_move_pos)
            self.start_move_pos = pos_
            e.accept()

    self.ui.topBar.mouseMoveEvent = move_window
    self.ui.status.mouseMoveEvent = move_window
    self.ui.toolBar.mouseMoveEvent = move_window
    self.container.ui.navi_header.mouseMoveEvent = move_window

    def double_click_maximize_restore(e: QMouseEvent):
        if e.type() == QEvent.Type.MouseButtonDblClick:
            maximize_restore()

    self.ui.topBar.mouseDoubleClickEvent = double_click_maximize_restore

    return maximize_restore

def resize_grips(self):
    self.grips['left_grip'].setGeometry(0, 10, 10, self.height()-10)
    self.grips['right_grip'].setGeometry(self.width() - 10, 10, 10, self.height()-10)
    self.grips['top_grip'].setGeometry(0, 0, self.width(), 10)
    self.grips['bottom_grip'].setGeometry(0, self.height() - 10, self.width(), 10)

def apply_style(app: QApplication, theme: str, to_save: bool = False):
    params = None
    qss = None

    app.setWindowIcon(QIcon(str(resources.path("qss", "art_explode.ico"))))

    def get_qss_theme():
        nonlocal params
        nonlocal qss
        qss = resources.read_text("qss", '.'.join((theme, "qss")))
        params = resources.read_text("qss", '.'.join((theme, "param")))

    def param_substitution():
        for key, val in ag.qss_params.items():
            if val.startswith("$"):
                ag.qss_params[key] = ag.qss_params[val]

    def parse_params():
        nonlocal params
        params = [it.split('~') for it in params.split('\n') if it.startswith("$") and ('~' in it)]
        params.sort(key=lambda x: x[0], reverse=True)
        ag.qss_params = {key.strip():value.strip() for key,value in params}
        param_substitution()

    def translate_qss():
        nonlocal params
        nonlocal qss
        parse_params()
        for key, val in ag.qss_params.items():
            qss = qss.replace(key, val)

    def dyn_qss_add_lines(lines: list[str]):
        for line in lines:
            if line.startswith('##'):
                key, val = line.split('~')
                ag.dyn_qss[key[2:]].append(val)

    def extract_dyn_qss() -> int:
        nonlocal qss
        it = qss.find("/* END")
        aa: str = qss
        it2 = aa.find('##', it)
        lines = qss[it2:].split("\n")
        dyn_qss_add_lines(lines)
        return it

    def save_qss(out_file: str):
        """ save translated qss """
        from PyQt6.QtCore import QFile, QTextStream
        nonlocal qss
        flqss = QFile(out_file)
        flqss.open(QFile.WriteOnly)
        stream = QTextStream(flqss)
        stream << qss
        stream.flush()
        flqss.close()

    get_qss_theme()
    translate_qss()
    it = extract_dyn_qss()
    app.setStyleSheet(qss[:it])

    if to_save:
        save_qss("out-qss.log")
