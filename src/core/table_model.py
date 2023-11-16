from loguru import logger

from PyQt6.QtCore import (QAbstractTableModel, QModelIndex, Qt,
    QSortFilterProxyModel, pyqtSignal
    )

from . import db_ut


class ProxyModel(QSortFilterProxyModel):

    def __init__(self, parent=None):
        super().__init__(parent)

    def flags(self, index):
        if not index.isValid():
            return super().flags(index)

        return (
            (Qt.ItemFlag.ItemIsEditable |
             Qt.ItemFlag.ItemIsDragEnabled |
             super().flags(index))
            if self.sourceModel().headerData(index.column()) in (
                'rating', 'Pages', 'Published', 'File Name'
            )
            else (Qt.ItemFlag.ItemIsDragEnabled |
                  super().flags(index))
        )

    def update_opened(self, ts: int, index: QModelIndex):
        """
        update timestamp when file is opened
        ts - the unix epoch timestamp
        """
        self.sourceModel().update_opened(ts, self.mapToSource(index))

    def update_field_by_name(self, val, name: str, index: QModelIndex):
        self.sourceModel().update_field_by_name(val, name, self.mapToSource(index))

    def get_row_by_id(self, id: int) -> int:
        idx = self.sourceModel().get_index_by_id(id)
        return self.mapFromSource(idx).row()

    def get_user_data(self) -> list:
        return self.sourceModel().get_user_data()

class TableModel(QAbstractTableModel):

    model_data_changed = pyqtSignal(str)

    def __init__(self, parent=None, *args):
        super().__init__(parent)
        self.header = ()
        self.rows = []
        self.user_data = []

    def rowCount(self, parent=QModelIndex()):
        return len(self.rows)

    def columnCount(self, parent=None):
        return len(self.header)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if index.isValid():
            col = index.column()
            if col == 0 and role == Qt.ItemDataRole.ToolTipRole:
                return self.rows[index.row()][col]
            if role == Qt.ItemDataRole.DisplayRole:
                # len(row) > col; len=1 -> col=0; len=2 -> col=(0,1) etc
                if len(self.rows[index.row()]) > col:
                    if self.header[col] in ('Date of last note','Modified','Open Date',):
                        return self.rows[index.row()][col].toString("yyyy-MM-dd hh:mm")
                    if self.header[col] == 'Created':
                        return self.rows[index.row()][col].toString("yyyy-MM-dd")
                    if self.header[col] == 'Published':
                        return self.rows[index.row()][col].toString("yyyy-MM")
                    return self.rows[index.row()][col]
                return None
            elif role == Qt.ItemDataRole.EditRole:
                return self.rows[index.row()][col]
            elif role == Qt.ItemDataRole.UserRole:
                return self.user_data[index.row()]
            elif role == Qt.ItemDataRole.TextAlignmentRole:
                if col:
                    return Qt.AlignmentFlag.AlignRight
                return Qt.AlignmentFlag.AlignLeft

    def get_user_data(self):
        return self.user_data

    def append_row(self, row, user_data=None):
        self.rows.append(row)
        self.user_data.append(user_data)

    def removeRows(self, row, count=1, parent=QModelIndex()):
        self.beginRemoveRows(QModelIndex(), row, row + count - 1)
        del self.rows[row:row + count]
        del self.user_data[row:row + count]
        self.endRemoveRows()
        return True

    def headerData(self, section,
        orientation=Qt.Orientation.Horizontal,
        role=Qt.ItemDataRole.DisplayRole):
        if not self.header:
            return None
        if (orientation == Qt.Orientation.Horizontal
            and role == Qt.ItemDataRole.DisplayRole):
            return self.header[section]

    def setHeaderData(self, p_int, orientation, value, role=None):
        if isinstance(value, str):
            value = value.split(' ')
        self.header = value

    def setData(self, index, value, role):
        if role != Qt.ItemDataRole.EditRole:
            return False

        col = index.column()
        line = self.rows[index.row()]
        if col < 0 or col >= len(line):
            return False
        field = self.header[col]
        val = value.toSecsSinceEpoch() if field == 'Published' else value
        if field == 'File Name':
            field = 'filename'
        db_ut.update_files_field(self.user_data[index.row()].id, field, val)
        line[col] = value
        self.dataChanged.emit(index, index)
        if field == 'filename':
            self.model_data_changed.emit(value)
        return True

    def get_row(self, row):
        if row >= 0 & row < self.rowCount():
            return self.rows[row], self.user_data[row]
        return ()

    def get_index_by_id(self, id: int) -> QModelIndex:
        for i,ud in enumerate(self.user_data):
            if ud.id == id:
                return self.index(i, 0, QModelIndex())
        return QModelIndex()

    def update_opened(self, ts: int, index: QModelIndex):
        """
        ts - the unix epoch timestamp
        """
        if "Open#" in self.header:
            i = self.header.index("Open#")
            self.rows[index.row()][i] += 1
        if "Open Date" in self.header:
            i = self.header.index("Open Date")
            self.rows[index.row()][i].setSecsSinceEpoch(ts)

    def update_field_by_name(self, val, name: str, index: QModelIndex):
        if name in self.header:
            i = self.header.index(name)
            self.rows[index.row()][i] = val
