from loguru import logger

from PyQt6.QtGui import QMouseEvent,
from PyQt6.QtWidgets import QTreeView

from . import app_globals as ag, low_bk

def set_context_menu():
    """
    Set context menus for each widget
    :return:
    """
    ag.dir_list.customContextMenuRequested.connect(low_bk.dir_menu)
    ag.file_list.customContextMenuRequested.connect(low_bk.file_menu)
    ag.dir_list.mouseReleaseEvent = dir_mouse_release
    ag.dir_list.mousePressEvent = dir_mouse_press
    ag.file_list.mouseReleaseEvent = file_mouse_release
    ag.file_list.mousePressEvent = file_mouse_press

def file_mouse_press(e: QMouseEvent):
    super(QTreeView, ag.file_list).mousePressEvent(e)
    logger.info(f'{type(e)}')
    e.ignore()

def file_mouse_release(e: QMouseEvent):
    super(QTreeView, ag.file_list).mouseReleaseEvent(e)
    logger.info(f'{type(e)}')
    e.ignore()

def dir_mouse_press(e: QMouseEvent):
    logger.info(f'{e.type()}, {e.buttons()}')
    super(QTreeView, ag.dir_list).mousePressEvent(e)
    e.ignore()

def dir_mouse_release(e: QMouseEvent):
    logger.info(f'{e.type()}, {e.buttons()}')
    super(QTreeView, ag.dir_list).mouseReleaseEvent(e)
    e.ignore()
