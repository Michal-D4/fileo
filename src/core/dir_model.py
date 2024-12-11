from loguru import logger

from collections import defaultdict

from PyQt6.QtCore import QAbstractItemModel, QModelIndex, Qt

from . import db_ut, app_globals as ag
from .. import tug

class dirItem(object):
    def __init__(self, data: str, user_data: ag.DirData, parent=None):
        self.parentItem: dirItem = parent
        self.itemData = data
        self.children = []

        self.userData: ag.DirData = user_data

    def child(self, row):
        return self.children[row]

    def childCount(self):
        return len(self.children)

    def childNumber(self):
        if self.parentItem != None:
            return self.parentItem.children.index(self)
        return 0

    def columnCount(self):
        return 1

    def data(self):
        return self.itemData

    def user_data(self):
        return self.userData

    def insertChildren(self, position, count, columns):
        if position < 0 or position > len(self.children):
            return False

        for row in range(count):
            data = [None for v in range(columns)]
            item = dirItem(data, None, self)
            self.children.insert(position, item)

        return True

    def appendChild(self, item: 'dirItem'):
        item.parentItem = self
        item.userData.parent_id = self.userData.id
        self.children.append(item)

    def parent(self):
        return self.parentItem

    def removeChildren(self, position, count):
        if position < 0 or position + count > len(self.children):
            return False

        for row in range(count):
            self.children.pop(position)

        return True

    def setData(self, value, role=Qt.ItemDataRole.EditRole):
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

        self.rootItem = dirItem(
            data='', user_data=ag.DirData(0, 0, False, False))

    def columnCount(self, parent=None):
        return 1

    def data(self, index, role: Qt.ItemDataRole):
        if (role == Qt.ItemDataRole.DisplayRole or
            role == Qt.ItemDataRole.EditRole):
            item = self.getItem(index)
            return item.data()
        elif role == Qt.ItemDataRole.ToolTipRole:
            u_dat = self.getItem(index).user_data()
            return u_dat.tool_tip
        elif role == Qt.ItemDataRole.UserRole:
            item = self.getItem(index)
            return item.user_data()
        elif role == Qt.ItemDataRole.DecorationRole:
            u_dat = self.getItem(index).user_data()
            if u_dat.hidden:
                return tug.get_icon("hidden")
            if u_dat.is_link:
                return tug.get_icon("link")
            return tug.get_icon("folder")

        return None

    def flags(self, index):
        if not index.isValid():
            return (Qt.ItemFlag.ItemIsDropEnabled | super().flags(index))

        return (
            Qt.ItemFlag.ItemIsEditable |
            Qt.ItemFlag.ItemIsDragEnabled |
            Qt.ItemFlag.ItemIsDropEnabled |
            super().flags(index))

    def getItem(self, index):
        if index.isValid():
            item = index.internalPointer()
            if item:
                return item

        return self.rootItem

    def index(self, row, column, parent: QModelIndex):
        if parent.isValid() and parent.column() != 0:
            return QModelIndex()

        parentItem = self.getItem(parent)
        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)

        return QModelIndex()

    def insertRows(self, position, rows, parent: QModelIndex):
        parentItem = self.getItem(parent)
        self.beginInsertRows(parent, position, position + rows - 1)
        success = parentItem.insertChildren(position, rows, 1)
        self.endInsertRows()

        return success

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()

        childItem = self.getItem(index)
        parentItem = childItem.parent()

        if parentItem == self.rootItem:
            return QModelIndex()
        return self.createIndex(parentItem.childNumber(), 0, parentItem)

    def removeRows(self, position, rows, parent: QModelIndex):
        parentItem = self.getItem(parent)

        self.beginRemoveRows(parent, position, position + rows - 1)
        success = parentItem.removeChildren(position, rows)
        self.endRemoveRows()

        return success

    def rowCount(self, parent: QModelIndex):
        parentItem = self.getItem(parent)

        return parentItem.childCount()

    def setData(self, index, value, role: Qt.ItemDataRole):
        logger.info(f'{role=}, {value=}')
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
            u_dat = row[-1]    # ag.DirData
            it = dirItem(data=row[1], user_data=u_dat)
            enroll_item(row[0], u_dat.id, it)

        for key in children:
            # sort by dir name case insensitive
            children[key].sort(key=lambda item: item.itemData[0].upper())
            parents[key].children = children[key]

    def restore_index(self, path):
        parent = QModelIndex()
        for id_ in path:
            idx = self.index(int(id_), 0, parent)
            parent = idx
        return parent

    def supportedDropActions(self) -> Qt.DropAction:
        return Qt.DropAction.CopyAction | Qt.DropAction.MoveAction

    def neighbor_idx(self, index: QModelIndex) -> QModelIndex:
        row = index.row()
        if row > 0:
            return self.index(row-1, 0, index.parent())

        if self.rowCount(index.parent()) > 1:
            return self.index(1, 0, index.parent())
        return index.parent()