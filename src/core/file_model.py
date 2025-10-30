# from loguru import logger
from pathlib import Path

from PyQt6.QtCore import (QAbstractTableModel, QModelIndex, Qt,
    QSortFilterProxyModel, QDateTime,
)
from PyQt6.QtWidgets import QStyle

from . import db_ut, app_globals as ag
from .. import tug

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

        return (  # is ItemIsEditable
            Qt.ItemFlag.ItemIsEditable | Qt.ItemFlag.ItemIsDragEnabled | super().flags(index)
            if self.sourceModel().is_editable(index.column()) else  # is not ItemIsEditable
            Qt.ItemFlag.ItemIsDragEnabled | super().flags(index)
        )

    def update_header(self, vals: str):
        model: fileModel = self.sourceModel()
        model.update_header(vals)

    def update_opened(self, ts: int, index: QModelIndex):
        self.sourceModel().update_opened(ts, self.mapToSource(index))

    def update_last_note_data(self, val, index: QModelIndex):
        self.sourceModel().update_last_note_data(val, self.mapToSource(index))

    def get_index_by_id(self, id: int) -> int:
        idx = self.sourceModel().get_index_by_id(id)
        return self.mapFromSource(idx)

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
        self.field_names = tug.qss_params['$FileListFields']
        self.editable = tug.qss_params['$Editable']
        self.field_type = tug.qss_params['$FieldTypes']
        self.tool_tip = tug.qss_params['$ToolTips']
        self.formats = tug.qss_params['$FieldFormats']
        self.rows = []
        self.user_data: list[int] = []  # file_id

    def update_header(self, vals: str):
        def convert_to_str():
            for i in range(len(self.rows)):
                self.rows[i][ii] = ''

        def convert_to_int():
            for i in range(len(self.rows)):
                self.rows[i][ii] = 0

        def convert_to_date():
            for i in range(len(self.rows)):
                self.rows[i][ii] = ag.DATE_1970_1_1

        def convert():
            if typ == 'str':
                convert_to_str()
            elif typ == 'int':
                convert_to_int()
            elif typ == 'date':
                convert_to_date()
            self.dataChanged.emit(self.index(0, ii), self.index(self.rowCount()-1, ii), [Qt.ItemDataRole.DisplayRole])

        idx, name, typ, old_typ, tip, fmt = vals.split('ё')    # ё most impossible symbol in title & toolTip
        ii = int(idx)
        if name != self.field_names[ii]:
            self.field_names[ii] = name
            ag.save_db_settings(FileListFields = self.field_names)
            self.headerDataChanged.emit(Qt.Orientation.Horizontal, ii, ii)

        if typ != old_typ:
            convert()
            self.field_type[ii] = typ
            ag.save_db_settings(FieldTypes = self.field_type)

        if tip != self.tool_tip[ii]:
            self.tool_tip[ii] = tip
            ag.save_db_settings(ToolTips = self.tool_tip)

        if fmt != self.formats[ii]:
            self.formats[ii] = fmt
            ag.save_db_settings(FieldFormats = self.formats)

    def is_editable(self, column: int) -> bool:
        return self.editable & 1 << column

    def rowCount(self, parent=None):
        return len(self.rows)

    def columnCount(self, parent=None):
        return len(self.field_names)

    def data(self, index, role: Qt.ItemDataRole):
        if index.isValid():
            col = index.column()
            line = self.rows[index.row()]
            if col == 0 and role == Qt.ItemDataRole.ToolTipRole:
                return line[col]
            if role == Qt.ItemDataRole.DisplayRole:
                if self.formats[col] and isinstance(line[col], QDateTime):
                    return line[col].toString(self.formats[col])
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

    def append_row(self, row:list, file_id: int=0):
        self.rows.append(row)
        self.user_data.append(file_id)

    def insertRows(self, row: int, count: int, parent: QModelIndex=QModelIndex()):
        self.beginInsertRows(parent, row, row + count - 1)
        if 0 > row > len(self.rows):
            success = False
        else:
            date0 = ag.DATE_1970_1_1
            for i in range(count):
                self.rows.insert(
                    row, ['<file_name>.md',date0,date0,0,0,date0,0,0,date0,date0,date0,('<file_name>','md')]
                )
                self.user_data.insert(row, 0)
            success = True
        self.endInsertRows()
        return success

    def index(self, row, column, parent: QModelIndex=QModelIndex()):
        if 0 > row or row >= len(self.rows):
            return QModelIndex()

        return self.createIndex(row, column, self.rows[row])

    def removeRows(self, row, count=1, parent=QModelIndex()):
        self.beginRemoveRows(QModelIndex(), row, row + count - 1)
        del self.rows[row:row + count]
        del self.user_data[row:row + count]
        self.endRemoveRows()
        return True

    def headerData(self, section, orientation=Qt.Orientation.Horizontal, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            return self.field_names[section]
        if role == Qt.ItemDataRole.ToolTipRole:
            return self.tool_tip[section]

    def setData(self, index, value, role: Qt.ItemDataRole):
        if role != Qt.ItemDataRole.EditRole:
            return False

        def _rename_file(new_name: str) -> bool:
            def new_file():
                try:
                    new_path.touch(exist_ok=False)
                except (FileExistsError, OSError) as e:
                    ag.show_message_box('File already exists', f'{e}')
                    return

                try:
                    cre_time = QDateTime().fromSecsSinceEpoch(int(new_path.stat().st_birthtime))
                except AttributeError:
                    cre_time = QDateTime().fromSecsSinceEpoch(int(new_path.stat().st_ctime))
                line[1] = line[5] = line[10] = cre_time
                ff = [line[i].toSecsSinceEpoch() if isinstance(line[i], QDateTime)
                      else line[i] for i in (5,2,10,3,4,7,6,8,1,)]
                file_id, is_new_ext = db_ut.insert_file(('', new_name, *ff[:-1], path), ff[-1], ag.fileSource.CREATED.value)
                self.user_data[index.row()] = file_id
                dir_id = ag.dir_list.currentIndex().data(Qt.ItemDataRole.UserRole).dir_id
                db_ut.copy_file(file_id, dir_id)
                ag.signals.user_signal.emit(f"New file created\\{file_id}")
                if is_new_ext:
                    ag.signals.user_signal.emit("ext inserted")

            def old_file() -> bool:
                try:
                    Path(path).rename(new_path)
                except (FileExistsError, FileNotFoundError, PermissionError) as e:
                    ag.show_message_box(
                        'Error renaming file',
                        f'{e}',
                        icon=QStyle.StandardPixmap.SP_MessageBoxCritical
                    )
                    return False
                return True

            if file_id:
                path = db_ut.get_file_path(file_id)
                new_path = Path(path).parent / new_name
                ok = old_file()
            else:
                path = tug.get_app_setting('DEFAULT_FILE_PATH',
                    str(Path('~/fileo/files').expanduser()))
                new_path = Path(path) / new_name
                ok = False
                new_file()

            line[0] = new_name
            line[-1] = (
                (new_path.stem.lower(), new_path.suffix.lower())
                if new_path.suffix else
                (new_path.stem.lower(),)
            )
            ag.app.ui.current_filename.setText(new_name)
            return ok

        col = index.column()
        file_id = self.user_data[index.row()]
        line = self.rows[index.row()]
        if col < 0 or col >= len(line):
            return False
        field = tug.qss_params['$EditableFields'].get(col, '')
        if field == 'filename':
            if not _rename_file(value):
                return False
        else:
            line[col] = value
            if tug.qss_params['$FieldTypes'][col] == 'date':
                value = value.toSecsSinceEpoch()
        db_ut.update_files_field(file_id, field, value)
        self.dataChanged.emit(index, index)
        ag.add_recent_file(self.user_data[index.row()])
        return True

    def get_index_by_id(self, file_id: int) -> QModelIndex:
        for i,f_id in enumerate(self.user_data):
            if f_id == file_id:
                return self.index(i, 0, QModelIndex())
        return QModelIndex()

    def update_opened(self, ts: int, index: QModelIndex):
        """
        ts - the unix epoch timestamp
        """
        if "Open#" in self.field_names:
            i = self.field_names.index("Open#")
            self.rows[index.row()][i] += 1
        if "Open Date" in self.field_names:
            i = self.field_names.index("Open Date")
            self.rows[index.row()][i].setSecsSinceEpoch(ts)

    def update_last_note_data(self, val, index: QModelIndex):
        self.rows[index.row()][9] = val

    def fill_model(self, files):
        def field_val():
            if typ == "str":
                return val if val else ''
            if typ == "int":
                try:
                    ret = int(val)
                except ValueError:
                    ret = 0
                return ret
            a = QDateTime()
            a.setSecsSinceEpoch(val) if isinstance(val, int) else ag.DATE_1970_1_1
            return a

        for ff in files:
            if not ff[0]:
                continue
            ff1 = []
            for typ, name, val in zip(tug.qss_params['$FieldTypes'], tug.qss_params['$FileListFields'], ff[:-1]):
                ff1.append(
                    ag.human_readable_size(val) if name == 'Size' else field_val()
                )

            filename = Path(ff[0])
            ff1.append(
                (filename.stem.lower(), filename.suffix.lower())
                if filename.suffix else
                (filename.stem.lower(),)
            )
            self.append_row(ff1, ff[-1])   # ff[-1] - file_id
