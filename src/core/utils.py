from loguru import logger

from pathlib import Path
from typing import Any, Optional
from importlib import resources

from PyQt6.QtCore import QEvent, Qt, QSettings, QVariant, QFile, QTextStream
from PyQt6.QtGui import QMouseEvent, QPixmap
from PyQt6.QtWidgets import QApplication, QMessageBox

from . import icons, app_globals as ag
from .. import qss as style_sheets

APP_NAME = "fileo"
MAKER = 'miha'

settings = None


def get_app_setting(key: str, default: Optional[Any]=None) -> QVariant:
    """
    used to restore settings on application level
    """
    global settings
    if not settings:
        settings = QSettings(MAKER, APP_NAME)
    try:
        to_set = settings.value(key, default)
    except (TypeError, SystemError) as e:
        # logger.info(f'{type(e)}, {e=}')
        to_set = default
    # logger.info(f'{key=}, {default=}, {to_set=}')
    return to_set

def save_app_setting(**kwargs):
    """
    used to save settings on application level
    """
    if not kwargs:
        return
    global settings
    if not settings:
        settings = QSettings(MAKER, APP_NAME)

    for key, value in kwargs.items():
        settings.setValue(key, QVariant(value))

def setup_ui(self):
    from ..widgets.custom_grips import CustomGrip

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

def save_to_file(filename: str, msg: str):
    """ save translated qss """
    pp = Path('~/fileo/report').expanduser()
    path = get_app_setting(
        'DEFAULT_REPORT_PATH', pp.as_posix()
    )
    path = Path(path) / filename

    flqss = QFile(path.as_posix())
    flqss.open(QFile.WriteOnly)
    stream = QTextStream(flqss)
    stream << msg
    stream.flush()
    flqss.close()

def apply_style(app: QApplication, theme: str, to_save: bool = False):
    params = None
    qss = None

    with resources.path(style_sheets, "search.svg") as pic_path:
        res_path = pic_path.parent.as_posix()

    def get_qss_theme():
        nonlocal params
        nonlocal qss
        qss = resources.read_text(style_sheets, '.'.join((theme, "qss")))
        params = resources.read_text(style_sheets, '.'.join((theme, "param")))

    def param_substitution():
        for key, val in ag.qss_params.items():
            if key.startswith("$ico_"):
                ag.qss_params[key] = '/'.join((res_path, val))
            elif key.startswith("$"):
                ag.qss_params[key] = val

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

    get_qss_theme()
    translate_qss()
    it = extract_dyn_qss()
    app.setStyleSheet(qss[:it])

    if to_save:
        save_to_file('QSS.log', qss)

    icons.collect_all_icons()

    icons.add_other_icon(
        'search', QPixmap(ag.qss_params['$ico_search'])
    )
    icons.add_other_icon(
        'match_case', QPixmap(ag.qss_params['$ico_match_case'])
    )
    icons.add_other_icon(
        'match_word', QPixmap(ag.qss_params['$ico_match_word'])
    )
    icons.add_other_icon(
        'app', QPixmap(ag.qss_params['$ico_app'])
    )

    try:
        from ctypes import windll  # to show icon on the taskbar - Windows only
        myappid = '.'.join((MAKER, APP_NAME))
        windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except ImportError:
        pass

    app.setWindowIcon(icons.get_other_icon("app"))

def show_message_box(title: str, msg: str,
                     btn: QMessageBox.StandardButton = QMessageBox.StandardButton.Close,
                     icon: QMessageBox.Icon = QMessageBox.Icon.Information,
                     details: str = '') -> int:
    dlg = QMessageBox(ag.app)
    dlg.setWindowTitle(title)
    dlg.setText(msg)
    dlg.setDetailedText(details)
    dlg.setStandardButtons(btn)
    dlg.setIcon(icon)
    return dlg.exec()
