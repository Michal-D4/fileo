from loguru import logger

from collections import defaultdict

from PyQt6.QtCore import QAbstractItemModel, QModelIndex, Qt

from . import db_ut, app_globals as ag
from .. import tug

class dirItem(object):
    def __init__(self, data: str, user_data: ag.DirData, parent=None):
        self.parentItem: dirItem = parent
        self.itemData = data
        self.children: list[dirItem] = []

        self.userData: ag.DirData = user_data

    def child(self, row) -> 'dirItem':
        return self.children[row] if self.children else None

    def childCount(self) -> int:
        return len(self.children)

    def childNumber(self) -> int:
        if self.parentItem is not None:
            return self.parentItem.children.index(self)
        return 0

    def columnCount(self) -> int:
        return 1

    def data(self) -> str:
        return self.itemData

    def user_data(self) -> ag.DirData:
        return self.userData

    def insertChildren(self, row: int, count: int, columns: int=1) -> bool:
        if row < 0 or row > len(self.children):
            return False

        for _ in range(count):
            item = dirItem('', None, self)
            self.children.insert(row, item)
        return True

    def appendChild(self, item: 'dirItem'):
        item.parentItem = self
        item.userData.parent = self.userData.dir_id
        self.children.append(item)

    def parent(self) -> 'dirItem':
        return self.parentItem

    def removeChildren(self, position, count) -> bool:
        if position < 0 or position + count > len(self.children):
            return False

        for row in range(count):
            self.children.pop(position)

        return True

    def setData(self, value, role=Qt.ItemDataRole.EditRole) -> bool:
        if role == Qt.ItemDataRole.ToolTipRole:
            self.userData.tool_tip = value
            db_ut.update_tooltip(self.userData)
            return True
        if role == Qt.ItemDataRole.EditRole:
            self.itemData = value
            db_ut.update_dir_name(value, self.userData)
            return True

    def setUserData(self, user_data: ag.DirData):
        self.userData = user_data


class dirModel(QAbstractItemModel):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.rootItem = dirItem(data='', user_data=ag.DirData(0, 0))

    def columnCount(self, parent=None) -> int:
        return 1

    def data(self, index, role: Qt.ItemDataRole):
        if (role == Qt.ItemDataRole.DisplayRole or
            role == Qt.ItemDataRole.EditRole):
            return self.getItem(index).data()
        elif role == Qt.ItemDataRole.ToolTipRole:
            return self.getItem(index).user_data().tool_tip
        elif role == Qt.ItemDataRole.UserRole:
            return self.getItem(index).user_data()
        elif role == Qt.ItemDataRole.DecorationRole:
            u_dat = self.getItem(index).user_data()
            if u_dat.multy:
                return (tug.get_icon("mult_hidden") if u_dat.hidden
                        else tug.get_icon("mult_folder"))
            return (tug.get_icon("hidden") if u_dat.hidden
                    else tug.get_icon("folder"))

        return None

    def flags(self, index):
        if not index.isValid():
            return (Qt.ItemFlag.ItemIsDropEnabled | super().flags(index))

        return (
            Qt.ItemFlag.ItemIsEditable |
            Qt.ItemFlag.ItemIsDragEnabled |
            Qt.ItemFlag.ItemIsDropEnabled |
            super().flags(index))

    def getItem(self, index) -> dirItem:
        if index.isValid():
            item = index.internalPointer()
            if item:
                return item

        return self.rootItem

    def index(self, row, column, parent: QModelIndex) -> QModelIndex:
        if parent.isValid() and parent.column() != 0:
            return QModelIndex()

        parentItem = self.getItem(parent)
        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)

        return QModelIndex()

    def insertRows(self, row: int, count: int, parent: QModelIndex) -> bool:
        parentItem = self.getItem(parent)
        self.beginInsertRows(parent, row, row + count - 1)
        success = parentItem.insertChildren(row, count)
        self.endInsertRows()
        return success

    def parent(self, index) -> QModelIndex:
        if not index.isValid():
            return QModelIndex()

        item = self.getItem(index)
        parentItem = item.parent()

        if parentItem is self.rootItem:
            return QModelIndex()
        return self.createIndex(parentItem.childNumber(), 0, parentItem)

    def removeRows(self, position, rows, parent: QModelIndex) -> bool:
        parentItem = self.getItem(parent)

        self.beginRemoveRows(parent, position, position + rows - 1)
        success = parentItem.removeChildren(position, rows)
        self.endRemoveRows()

        return success

    def rowCount(self, parent=QModelIndex()):
        parentItem = self.getItem(parent)

        return parentItem.childCount()

    def setData(self, index, value, role: Qt.ItemDataRole) -> bool:
        if role != Qt.ItemDataRole.EditRole and role != Qt.ItemDataRole.ToolTipRole:
            return False

        item = self.getItem(index)
        return item.setData(value, role)

    def set_model_data(self):
        """
        Fill dir tree structure
        :return: None
        """
        dirs = db_ut.dir_tree_select()
        # dirs in such an order that the parent
        # goes before its children
        # structure: parent key; dir name, ag.DirData

        children = defaultdict(list)
        parents = {'0': self.rootItem}

        def enroll_item(key: str, id: int, item: dirItem):
            item.parentItem = parents[key]
            parents[','.join((key, str(id)))] = item
            children[key].append(item)

        for row in dirs:
            u_dat: ag.DirData = row[-1]
            item = dirItem(data=row[1], user_data=u_dat)
            enroll_item(row[0], u_dat.dir_id, item)

        for key in children:
            # set children sorted by dir name case insensitive
            children[key].sort(key=lambda item: item.itemData[0].lower())
            parents[key].children = children[key]
        logger.info(f'{len(parents)=}, {len(children)=}')

    def restore_index(self, path) -> QModelIndex:
        parent = QModelIndex()
        for id_ in path:
            idx = self.index(int(id_), 0, parent)
            parent = idx
        return parent
