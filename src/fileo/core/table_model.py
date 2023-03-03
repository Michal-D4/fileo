from collections.abc import Iterable

from PyQt6.QtCore import (QAbstractTableModel, QModelIndex, Qt,
    QMimeData, QByteArray, QDataStream, QIODevice,
    QSortFilterProxyModel,
    )

from core import app_globals as ag, db_ut


class ProxyModel(QSortFilterProxyModel):

    def __init__(self, parent=None):
        super().__init__(parent)

    def delete_row(self, index):
        self.sourceModel().delete_row(self.mapToSource(index))

    def setHeaderData(self, value):
        self.sourceModel().setHeaderData(0, Qt.Orientation.Horizontal, value)

    def get_headers(self):
        return self.sourceModel().header

    def rowCount(self, parent=QModelIndex()):
        return self.sourceModel().rowCount(parent)


class ProxyModel2(ProxyModel):
    """
    Specific model for file list:
    reimplemened mimeData, mimeTypes, flags methods
    """

    def __init__(self, parent=None):
        super().__init__(parent)

    def flags(self, index):
        if not index.isValid():
            return super().flags(index)

        return (
            (Qt.ItemFlag.ItemIsEditable | Qt.ItemFlag.ItemIsDragEnabled | super().flags(index))
            if self.sourceModel().headerData(index.column()) in ('rating', 'Pages', 'Published')
            else (Qt.ItemFlag.ItemIsDragEnabled | super().flags(index))
        )

    def mimeTypes(self):
        return ag.mimeType.files

    def mimeData(self, indexes):
        item_data = QByteArray()
        data_stream = QDataStream(item_data, QIODevice.WriteOnly)

        data_stream.writeInt(len(indexes))
        tmp = None
        for idx in indexes:
            s_idx = self.mapToSource(idx)
            tmp = self.sourceModel().data(s_idx, role=Qt.ItemDataRole.UserRole)
            data_stream.writeInt(tmp.file_id)    # file ID
            # may need, in case of copy/move for real folder using mimeData
            data_stream.writeInt(tmp.dir_id)

        mime_data = QMimeData()
        mime_data.setData(ag.mimeType.files, item_data)
        return mime_data

    def update_opened(self, ts: int, index: QModelIndex):
        self.sourceModel().update_opened(ts, self.mapToSource(index))

    def update_field_by_name(self, val, name: str, index: QModelIndex):
        self.sourceModel().update_field_by_name(val, name, self.mapToSource(index))


class TableModel(QAbstractTableModel):
    def __init__(self, parent=None, *args):
        super(TableModel, self).__init__(parent)
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
                # row length > current column
                if len(self.rows[index.row()]) > col:
                    if self.header[col] in ('Commented','Modified','Open Date',):
                        return self.rows[index.row()][col].toString("yyyy-MM-dd hh:mm")
                    if self.header[col] == 'Created':
                        return self.rows[index.row()][col].toString("yyyy-MM-dd")
                    if self.header[col] == 'Published':
                        return self.rows[index.row()][col].toString("MMM yyyy")
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

    def delete_row(self, index):
        if index.isValid():
            row = index.row()
            self.beginRemoveRows(QModelIndex(), row, row)
            self.rows.remove(self.rows[row])
            self.user_data.remove(self.user_data[row])
            self.endRemoveRows()

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
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
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
        if col < 1 or col >= len(line):
            return False
        header = self.header[index.column()]
        val = value.toSecsSinceEpoch() if self.header[col] == 'Published' else value
        db_ut.update_files_field(self.user_data[index.row()].id, header, val)
        line[col] = value
        self.dataChanged.emit(index, index)
        return True

    def get_row(self, row):
        if row >= 0 & row < self.rowCount():
            return self.rows[row], self.user_data[row]
        return ()

    def update_opened(self, ts: int, index: QModelIndex):
        """
        ts - timestamp
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
