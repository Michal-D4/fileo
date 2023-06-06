from . import app_globals as ag, low_bk

def set_context_menu():
    """
    Set context menus for each widget
    :return:
    """
    ag.dir_list.customContextMenuRequested.connect(low_bk.dir_menu)
    ag.file_list.customContextMenuRequested.connect(low_bk.file_menu)
