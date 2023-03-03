from loguru import logger
from collections import deque

from PyQt6.QtCore import (Qt, pyqtSlot, QMimeData, QByteArray,
    QModelIndex, QDataStream, QIODevice,
)
from PyQt6.QtGui import (QDrag, QDragMoveEvent, QDropEvent, QDragEnterEvent,
)


from . import app_globals as ag, low_bk, load_files, db_ut
from .edit_tree_model2 import get_index_path, TreeItem

dragged_ids = None

def get_files_mime_data() -> QMimeData:
    indexes = ag.file_list.selectionModel().selectedRows()
    return file_mime_data(indexes)

def file_mime_data(indexes) -> QMimeData:
    """
    mimedata contains:
    - number of selected files
    - for each file: id, dir_id
    """
    model = ag.file_list.model()
    drag_data = QByteArray()
    data_stream = QDataStream(drag_data, QIODevice.OpenModeFlag.WriteOnly)

    data_stream.writeInt(len(indexes))
    for idx in indexes:
        s_idx = model.mapToSource(idx)
        u_dat = model.sourceModel().data(s_idx, role=Qt.ItemDataRole.UserRole)
        data_stream.writeInt(u_dat.id)
        data_stream.writeInt(u_dat.dir_id)

    mime_data = QMimeData()
    mime_data.setData(ag.mimeType.files.value, drag_data)
    return mime_data

def get_dir_mime_data() -> QMimeData:
    global dragged_ids

    indexes = ag.dir_list.selectionModel().selectedRows()
    dragged_ids = get_dragged_ids(indexes)
    return dir_mime_data(indexes)

def get_dragged_ids(indexes: QModelIndex):
    """
    save full tree of dragged dirs
    used in bk_ut.is_descendant() method
    to reject dragging if a loop is created in the tree
    """
    model = ag.dir_list.model()
    ids = []

    qu = deque()
    qu.extend(indexes)
    while qu:
        idx = qu.pop()
        ids.append(idx.data(Qt.ItemDataRole.UserRole).id)
        n = model.rowCount(idx)
        for i in range(n):
            qu.append(model.index(i, 0, idx))
    return set(ids)

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

@pyqtSlot(Qt.DropAction)
def start_drag_dirs(dummy):
    drag = QDrag(ag.app)

    mime_data = get_dir_mime_data()
    drag.setMimeData(mime_data)
    bb = drag.exec(
        Qt.DropAction.CopyAction | Qt.DropAction.MoveAction
        if ag.mode is ag.appMode.DIR else Qt.DropAction.CopyAction,
        Qt.DropAction.CopyAction)

    if bb is not Qt.DropAction.IgnoreAction:
        low_bk.reload_dirs_changed(ag.drop_target, ag.dropped_ids[0])

@pyqtSlot(Qt.DropAction)
def start_drag_files(dummy):
    drag = QDrag(ag.app)

    mime_data = get_files_mime_data()
    drag.setMimeData(mime_data)
    drag.exec(
        Qt.DropAction.CopyAction | Qt.DropAction.MoveAction,
        Qt.DropAction.CopyAction)

    if ag.drop_action is Qt.DropAction.MoveAction:
        low_bk.files_from_folder()

@pyqtSlot(QDragEnterEvent)
def drag_enter_event(event: QDragEnterEvent):
    """
    set DropAction depending on pressed MouseButton:
    LeftButton -> CopyAction; RightButton -> MoveAction
    """
    if event.buttons() is Qt.MouseButton.RightButton:
        ag.drop_action = Qt.DropAction.MoveAction
        event.setDropAction(ag.drop_action)
    elif event.buttons() is Qt.MouseButton.LeftButton:
        ag.drop_action = Qt.DropAction.CopyAction
    event.accept()

@pyqtSlot(QDragMoveEvent)
def drag_move_event(event: QDragMoveEvent):
    mime_data: QMimeData = event.mimeData()
    if event.dropAction() is Qt.DropAction.IgnoreAction:
        event.ignore()
        return

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
def drop_event(event: QDropEvent):
    pos = event.position().toPoint()
    index = ag.dir_list.indexAt(pos)

    id = (
        index.data(role=Qt.ItemDataRole.UserRole).id
        if index.isValid() else 0
    )
    if drop_data(event.mimeData(), ag.drop_action, id):
        ag.drop_target = index
        event.accept()
    else:
        ag.drop_action = Qt.DropAction.IgnoreAction
        event.ignore()

def drop_data(data: QMimeData, act: Qt.DropAction, target: int) -> bool:
    if data.hasFormat('text/uri-list'):
        return drop_uri_list(data, target)

    if data.hasFormat(ag.mimeType.files.value):
        return drop_files(data, act, target)

    if data.hasFormat(ag.mimeType.folders.value):
        return drop_folders(data, act, target)

    return False

def drop_uri_list(data: QMimeData, target: int) -> bool:
    load = load_files.loadFiles()
    load.set_files_iter(
        (it.toLocalFile() for it in data.urls())
    )
    load.load_to_dir(target)
    return True

def drop_files(data: QMimeData, act: Qt.DropAction, target: int) -> bool:
    if act is Qt.DropAction.CopyAction:
        return copy_files(data, target)
    if act is Qt.DropAction.MoveAction:
        return move_files(data, target)
    return False

def copy_files(data: QMimeData, target: int) -> bool:
    files_data = data.data(ag.mimeType.files.value)
    stream = QDataStream(files_data, QIODevice.OpenModeFlag.ReadOnly)

    count = stream.readInt()

    for _ in range(count):
        id = stream.readInt()
        _ = stream.readInt()   # dir_id; don't use here
        db_ut.copy_file(id, target)

    return True

def move_files(data: QMimeData, target: int) -> bool:
    files_data = data.data(ag.mimeType.files.value)
    stream = QDataStream(files_data, QIODevice.OpenModeFlag.ReadOnly)

    count = stream.readInt()

    for _ in range(count):
        id = stream.readInt()
        dir_id = stream.readInt()
        if not dir_id:
            dir_id = db_ut.get_dir_id_for_file(id)
        if dir_id:
            db_ut.move_file(target, dir_id, id)
        else:
            db_ut.copy_file(id, target)
    return True

def drop_folders(data: QMimeData, act: Qt.DropAction, target: int) -> bool:
    ag.dropped_ids.clear()
    copy_move = (
        move_folder if act is Qt.DropAction.MoveAction
        else copy_folder
    )

    folders_data = data.data(ag.mimeType.folders.value)
    stream = QDataStream(folders_data, QIODevice.ReadOnly)
    idx_count = stream.readInt()
    model = ag.dir_list.model()
    for _ in range(idx_count):
        tmp_str = stream.readQString()
        id_list = (int(i) for i in tmp_str.split(','))
        idx = model.restore_index(id_list)
        if not copy_move(idx, target):
            return False
    return True

def copy_folder(index: QModelIndex, target: int) -> bool:
    dir_id = index.data(Qt.ItemDataRole.UserRole).id
    ag.dropped_ids.append(dir_id)

    db_ut.copy_dir(target, dir_id)
    return True

def move_folder(index: QModelIndex, target: int) -> bool:
    u_dat = index.data(Qt.ItemDataRole.UserRole)
    ag.dropped_ids.append(u_dat.id)

    if db_ut.move_dir(target, u_dat.parent_id, u_dat.id):
        return True
    return False
