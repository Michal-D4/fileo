from loguru import logger
from collections import deque

from PyQt6.QtCore import (Qt, QMimeData, QByteArray, QModelIndex,
    QDataStream, QIODevice, )

from . import app_globals as ag
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
