from PyQt6.QtCore import pyqtSignal, QObject
from PyQt6.QtWidgets import QWidget


class AppSignals(QObject):

    get_db_name = pyqtSignal(str, name="get_db_name")

    filter_setup_closed = pyqtSignal(name="filter_setup_closed")

    collapseSignal = pyqtSignal(QObject, bool)
    hideSignal = pyqtSignal(bool, int)

    start_disk_scanning = pyqtSignal(str, list, name="start_disk_scanning")

    user_signal = pyqtSignal(str, name="user_signal")

    app_mode_changed = pyqtSignal(int)

    delete_note = pyqtSignal(QWidget)

    start_edit_note = pyqtSignal(QWidget)

    refresh_note_list = pyqtSignal()

    color_theme_changed = pyqtSignal()
