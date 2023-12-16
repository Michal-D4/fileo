from loguru import logger
from collections import deque
import sys

from PyQt6.QtCore import (Qt, pyqtSlot, QMimeData, QByteArray,
    QModelIndex, QDataStream, QIODevice, QCoreApplication,
    QTextStream,
)
from PyQt6.QtGui import (QDrag, QDragMoveEvent, QDropEvent, QDragEnterEvent,
)
from . import app_globals as ag, low_bk, load_files, db_ut
from .edit_tree_model2 import TreeItem, TreeModel

if sys.platform.startswith("win"):
    from . import win_menu as menu
elif sys.platform.startswith("linux"):
    from . import linux_menu as menu
else:
    raise ImportError(f"doesn't support {sys.platform} system")

drop_target: QModelIndex = QModelIndex()
dragged_ids = []
dropped_ids = []

def get_index_path(index: QModelIndex) -> list[int]:
    """
    for index returns the full path from root to this index
    """
    idx = index
    path = []
    while idx.isValid():
        path.append(idx.row())
        idx = idx.parent()
    path.reverse()
    return path

def get_files_mime_data() -> QMimeData:
    indexes = ag.file_list.selectionModel().selectedRows()
    return file_mime_data(indexes)

def file_mime_data(indexes) -> QMimeData:
    """
    mimedata contains:
    - Pid of current instance
    - number of selected files
    - for each file: id, dir_id
    """
    drag_data = QByteArray()
    data_stream = QDataStream(drag_data, QIODevice.OpenModeFlag.WriteOnly)
    pid = QCoreApplication.applicationPid()
    data_stream.writeInt(pid)

    if ag.mode is ag.appMode.DIR or ag.filter_dlg.is_single_folder():
        dir_idx = ag.dir_list.currentIndex()
        dir_id = dir_idx.data(Qt.ItemDataRole.UserRole).id
    else:
        dir_id = 0

    data_stream.writeInt(dir_id)
    data_stream.writeInt(len(indexes))
    model = ag.file_list.model()
    for idx in indexes:
        s_idx = model.mapToSource(idx)
        data_stream.writeInt(
            model.sourceModel().data(
                s_idx, role=Qt.ItemDataRole.UserRole
            ).id
        )

    mime_data = QMimeData()
    mime_data.setData(ag.mimeType.files_in.value, drag_data)
    mime_data.setData(
        ag.mimeType.files_out.value,
        external_file_list(indexes)
    )
    return mime_data

def external_file_list(indexes) ->QMimeData:
    """
    create QMimeData to drag to another instance
    .QtCore.QCoreApplication.applicationPid()
    """
    drag_data = QByteArray()
    data_stream = QTextStream(drag_data, QIODevice.OpenModeFlag.WriteOnly)
    low_bk._export_files(data_stream)

    return drag_data

def get_dir_mime_data() -> QMimeData:

    indexes = ag.dir_list.selectionModel().selectedRows()
    get_dragged_ids(indexes)
    return dir_mime_data(indexes)

def get_dragged_ids(indexes: QModelIndex):
    """
    save full tree of dragged dirs
    used in bk_ut.is_descendant() method
    to reject dragging if a loop is created in the tree
    """
    model = ag.dir_list.model()
    dragged_ids.clear()
    ids = []

    qu = deque()
    qu.extend(indexes)
    while qu:
        idx = qu.pop()
        ids.append(idx.data(Qt.ItemDataRole.UserRole).id)
        n = model.rowCount(idx)
        for i in range(n):
            qu.append(model.index(i, 0, idx))
    dragged_ids.extend(set(ids))

def dir_mime_data(indexes) -> QMimeData:
    """
    returns mime_data with paths from root to each selected dir
    """
    drag_data = QByteArray()
    data_stream = QDataStream(drag_data, QIODevice.OpenModeFlag.WriteOnly)

    data_stream.writeInt(len(indexes))
    for idx in indexes:
        it: TreeItem = idx.internalPointer()
        path = get_index_path(idx)
        data_stream.writeQString(','.join((str(x) for x in path)))

    mime_data = QMimeData()
    mime_data.setData(ag.mimeType.folders.value, drag_data)
    return mime_data

def set_drag_drop_handlers():
    ag.dir_list.startDrag = start_drag_dirs
    ag.file_list.startDrag = start_drag_files
    ag.dir_list.dragMoveEvent = drag_move_event
    ag.dir_list.dragEnterEvent = drag_enter_event
    ag.dir_list.dropEvent = drop_event

@pyqtSlot(Qt.DropAction)
def start_drag_dirs(action):
    drag = QDrag(ag.app)

    mime_data = get_dir_mime_data()
    drag.setMimeData(mime_data)
    bb = drag.exec(
        Qt.DropAction.CopyAction | Qt.DropAction.MoveAction
    )

    if bb is not Qt.DropAction.IgnoreAction:
        low_bk.reload_dirs_changed(drop_target, dropped_ids[0])

@pyqtSlot(Qt.DropAction)
def start_drag_files(action):
    drag = QDrag(ag.app)

    mime_data = get_files_mime_data()
    drag.setMimeData(mime_data)
    bb = drag.exec(
        Qt.DropAction.CopyAction | Qt.DropAction.MoveAction,
        Qt.DropAction.CopyAction)

    if bb is Qt.DropAction.MoveAction:
        low_bk.refresh_file_list()

@pyqtSlot(QDragEnterEvent)
def drag_enter_event(event: QDragEnterEvent):
    ag.drop_button = event.buttons()
    event.accept()

@pyqtSlot(QDragMoveEvent)
def drag_move_event(event: QDragMoveEvent):
    if event.dropAction() is Qt.DropAction.IgnoreAction:
        event.ignore()
        return

    mime_data: QMimeData = event.mimeData()
    if mime_data.hasFormat(ag.mimeType.folders.value):
        can_drop_dir_here(event)
    else:
        can_drop_file_here(event)

def can_drop_file_here(event: QDropEvent):
    """
    file can't be dropped in the root
    """
    index = ag.dir_list.indexAt(event.position().toPoint())
    if index.isValid():
        event.accept()
    else:
        event.ignore()

def can_drop_dir_here(event: QDropEvent):
    # doesn't matter if Qt.DropAction.MoveAction
    #                or Qt.DropAction.CopyAction:
    # target can't be child of source; to avoid loop in tree
    index = ag.dir_list.indexAt(event.position().toPoint())
    if is_descendant(index):
        event.ignore()
    else:
        event.accept()

def is_descendant(idx: QModelIndex) -> bool:
    parent_idx = idx
    while parent_idx.isValid():
        p_id = parent_idx.data(role=Qt.ItemDataRole.UserRole).id
        if p_id in dragged_ids:
            return True
        parent_idx = parent_idx.parent()
    return False

@pyqtSlot(QDropEvent)
def drop_event(e: QDropEvent):
    global drop_target
    menu.choose_drop_action(e)
    pos = e.position().toPoint()
    index = ag.dir_list.indexAt(pos)
    id = (
        index.data(role=Qt.ItemDataRole.UserRole).id
        if index.isValid() else 0
    )
    if drop_data(e.mimeData(), e.dropAction(), id):
        drop_target = index
        e.accept()
    else:
        e.setDropAction(Qt.DropAction.IgnoreAction)
        e.ignore()

def drop_data(data: QMimeData, act: Qt.DropAction, target: int) -> bool:
    if data.hasFormat(ag.mimeType.files_uri.value):
        drop_uri_list(data, target)
        update_file_list(target)
        return True

    if data.hasFormat(ag.mimeType.files_in.value):
        return drop_files(data, act, target)

    if data.hasFormat(ag.mimeType.folders.value):
        return drop_folders(data, act, target)

    return False

def update_file_list(target: int):
    idx = ag.dir_list.currentIndex()
    if idx.isValid():
        if ((ag.mode is ag.appMode.DIR or ag.filter_dlg.is_single_folder())
            and idx.data(Qt.ItemDataRole.UserRole).id == target):
            low_bk.refresh_file_list()

def drop_uri_list(data: QMimeData, target: int) -> bool:
    load = load_files.loadFiles()
    load.set_files_iterator(
        (it.toLocalFile() for it in data.urls())
    )
    load.load_to_dir(target)

def drop_files(data: QMimeData, act: Qt.DropAction, target: int) -> bool:
    files_data = data.data(ag.mimeType.files_in.value)
    stream = QDataStream(files_data, QIODevice.OpenModeFlag.ReadOnly)
    pid_from = stream.readInt()
    if QCoreApplication.applicationPid() == pid_from:
        if act is Qt.DropAction.CopyAction:
            return copy_files(stream, target)
        if act is Qt.DropAction.MoveAction:
            return move_files(stream, target)
        return False
    else:
        files_data = data.data(ag.mimeType.files_out.value)
        stream = QTextStream(files_data, QIODevice.OpenModeFlag.ReadOnly)
        low_bk._import_files(stream)

def copy_files(stream: QDataStream, target: int) -> bool:
    _ = stream.readInt()   # source dir_id - not used here
    count = stream.readInt()

    for _ in range(count):
        id = stream.readInt()
        db_ut.copy_file(id, target)

    return True

def move_files(stream: QDataStream, target: int) -> bool:
    dir_id = stream.readInt()   # source dir_id
    count = stream.readInt()

    for _ in range(count):
        file_id = stream.readInt()
        if not dir_id:
            dir_id = db_ut.get_dir_id_for_file(file_id)
        if dir_id:
            db_ut.move_file(target, dir_id, file_id)
        else:
            db_ut.copy_file(file_id, target)
    return True

def drop_folders(data: QMimeData, act: Qt.DropAction, target: int) -> bool:
    dropped_ids.clear()
    copy_move = (
        move_folder if act is Qt.DropAction.MoveAction
        else copy_folder
    )

    folders_data = data.data(ag.mimeType.folders.value)
    stream = QDataStream(folders_data, QIODevice.ReadOnly)
    idx_count = stream.readInt()
    model: TreeModel = ag.dir_list.model()
    for _ in range(idx_count):
        tmp_str = stream.readQString()
        id_list = (int(i) for i in tmp_str.split(','))
        idx = model.restore_index(id_list)
        if not copy_move(idx, target):
            return False
    return True

def copy_folder(index: QModelIndex, target: int) -> bool:
    dir_data = index.data(Qt.ItemDataRole.UserRole)
    dropped_ids.append(dir_data.id)

    db_ut.copy_dir(target, dir_data)
    return True

def move_folder(index: QModelIndex, target: int) -> bool:
    u_dat = index.data(Qt.ItemDataRole.UserRole)
    dropped_ids.append(u_dat.id)

    if db_ut.move_dir(target, u_dat.parent_id, u_dat.id):
        return True
    return False
