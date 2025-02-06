from pathlib import Path

from PyQt6.QtCore import (QAbstractTableModel, QModelIndex, Qt,
    QSortFilterProxyModel,
    )
from PyQt6.QtWidgets import QMessageBox

from . import db_ut, app_globals as ag

SORT_ROLE = Qt.ItemDataRole.UserRole + 1
SZ_SCALE = {
    'Kb': 1024,
    'Mb': 1048576,
    'Gb': 1073741824
}

class fileProxyModel(QSortFilterProxyModel):

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
                'rating', 'Pages', 'Published', 'File Name'   # ItemIsEditable
            )
            else  # is not ItemIsEditable
            (Qt.ItemFlag.ItemIsDragEnabled |
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

    def get_index_by_id(self, id: int) -> int:
        idx = self.sourceModel().get_index_by_id(id)
        return self.mapFromSource(idx)

    def get_user_data(self) -> list:
        return self.sourceModel().get_user_data()

    def lessThan(self, left: QModelIndex, right: QModelIndex) -> bool:
        if left.column() == 0:
            l_val = self.sourceModel().data(left, SORT_ROLE)
            r_val = self.sourceModel().data(right, SORT_ROLE)
            return l_val < r_val
        if self.sourceModel().headerData(left.column()) == 'Size':
            ll = self.sourceModel().data(left, Qt.ItemDataRole.DisplayRole)
            rr = self.sourceModel().data(right, Qt.ItemDataRole.DisplayRole)
            l_val = ll if isinstance(ll, int) else int(float(ll[:-3]) * SZ_SCALE[ll[-2:]])
            r_val = rr if isinstance(rr, int) else int(float(rr[:-3]) * SZ_SCALE[rr[-2:]])
            return l_val < r_val
        return super().lessThan(left, right)


class fileModel(QAbstractTableModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.header = ()
        self.rows = []
        self.user_data: list[ag.FileData] = []

    def rowCount(self, parent=None):
        return len(self.rows)

    def columnCount(self, parent=None):
        return len(self.header)

    def data(self, index, role: Qt.ItemDataRole):
        if index.isValid():
            col = index.column()
            line = self.rows[index.row()]
            if col == 0 and role == Qt.ItemDataRole.ToolTipRole:
                return line[col]
            if role == Qt.ItemDataRole.DisplayRole:
                # len(row) > col; len=1 -> col=0; len=2 -> col=(0,1) etc
                if len(line) > col:
                    if self.header[col] in ('Date of last note','Modified','Open Date',):
                        return line[col].toString("yyyy-MM-dd hh:mm")
                    if self.header[col] == 'Created':
                        return line[col].toString("yyyy-MM-dd")
                    if self.header[col] == 'Published':
                        return line[col].toString("MMM yyyy")
                    return line[col]
            elif role == Qt.ItemDataRole.EditRole:
                return line[col]
            elif role == Qt.ItemDataRole.UserRole:
                return self.user_data[index.row()]
            elif role == SORT_ROLE:
                return line[col] if col else line[-1]
            elif role == Qt.ItemDataRole.TextAlignmentRole:
                if col:
                    return Qt.AlignmentFlag.AlignRight
                return Qt.AlignmentFlag.AlignLeft
        return None

    def get_user_data(self):
        return self.user_data

    def append_row(self, row:list, user_data=ag.FileData()):
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
        self.header = value

    def setData(self, index, value, role: Qt.ItemDataRole):
        if role != Qt.ItemDataRole.EditRole:
            return False

        def _rename_file(new_name: str) -> bool:
            path = Path(db_ut.get_file_path(file_id))
            try:
                new_path = path.rename(path.parent / new_name)
                line[0] = new_name
                line[-1] = (
                    (new_path.stem.lower(), new_path.suffix.lower())
                    if new_path.suffix else
                    (new_path.stem.lower(),)
                )
                ag.app.ui.current_filename.setText(new_name)
                return True
            except (FileExistsError, FileNotFoundError) as e:
                ag.show_message_box(
                    'Error renaming file',
                    f'{e}',
                    icon=QMessageBox.Icon.Critical
                )
                return False

        col = index.column()
        file_id = self.user_data[index.row()].id
        line = self.rows[index.row()]
        if col < 0 or col >= len(line):
            return False
        field = self.header[col]
        if field == 'File Name':
            if not _rename_file(value):
                return False
            field = 'filename'
        else:
            line[col] = value
            if field == 'Published':
                value = value.toSecsSinceEpoch()
        db_ut.update_files_field(file_id, field, value)
        self.dataChanged.emit(index, index)
        ag.add_file_to_recent(self.user_data[index.row()].id)
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
