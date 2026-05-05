# from loguru import logger
from pathlib import Path

from PyQt6.QtCore import (QAbstractTableModel, QModelIndex, Qt,
    QSortFilterProxyModel, QDateTime, pyqtSlot
)
from PyQt6.QtWidgets import QStyle

from . import db_ut, app_globals as ag
from .. import tug
from ..widgets.cust_msgbox import show_message_box

SRT_IDX = -2
SORT_ROLE = Qt.ItemDataRole.UserRole + 1
SIZE_SORT_ROLE = Qt.ItemDataRole.UserRole + 2

def create_date_obj(val: int) -> QDateTime:
    d = QDateTime()
    d.setSecsSinceEpoch(val)
    return d

class fileProxyModel(QSortFilterProxyModel):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.rows = None
        self.user_data = None
        self.inserted_row = -1
        self.lessThan = self.normalLessThan
        self.field_names = ag.get_db_setting('FileListFields', tug.qss_params['$FileListFields'])
        self.editable = tug.qss_params['$Editable']

    def flags(self, index):
        if not index.isValid():
            return super().flags(index)

        return (  # is ItemIsEditable
            Qt.ItemFlag.ItemIsEditable | Qt.ItemFlag.ItemIsDragEnabled | super().flags(index)
            if (self.editable & 1 << index.column()) else  # is not ItemIsEditable
            Qt.ItemFlag.ItemIsDragEnabled | super().flags(index)
        )

    def set_inserted_row(self, val: int):
        if val >= 0:
            self.lessThan = self.new_file_lessThan
        else:
            self.lessThan = self.normalLessThan
        self.inserted_row = val
        self.sourceModel().set_inserted_row(val)

    def assign_source_data(self):
        self.rows = self.sourceModel().rows
        self.user_data = self.sourceModel().user_data

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

    def normalLessThan(self, left: QModelIndex, right: QModelIndex) -> bool:
        def get_col(col) -> int:
            if col == 0:
                sort_col = SRT_IDX
            elif self.field_names[col] == 'Size':
                sort_col = SRT_IDX+1
            else:
                sort_col = col
            return sort_col

        col = get_col(left.column())
        return self.rows[left.row()][col] < self.rows[right.row()][col]

    def new_file_lessThan(self, left: QModelIndex, right: QModelIndex) -> bool:
        def get_rows(idx: QModelIndex) -> tuple[int, int]:
            flag = 1
            row = idx.row()
            if self.user_data[row] == 0:
                flag = 0
                row += 1
            return row, flag

        def get_col(col) -> int:
            if col == 0:
                sort_col = SRT_IDX
            elif self.field_names[col] == 'Size':
                sort_col = SRT_IDX+1
            else:
                sort_col = col
            return sort_col

        lrow, lflag = get_rows(left)
        rrow, rflag = get_rows(right)
        col = get_col(left.column())

        l_val = (self.rows[lrow][col], lflag)
        r_val = (self.rows[rrow][col], rflag)

        return l_val < r_val


class fileModel(QAbstractTableModel):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.field_names = ag.get_db_setting('FileListFields', tug.qss_params['$FileListFields'])
        self.field_type = ag.get_db_setting('FieldTypes', tug.qss_params['$FieldTypes'])
        self.tool_tip = ag.get_db_setting('ToolTips', tug.qss_params['$ToolTips'])
        self.formats = ag.get_db_setting('FieldFormats', tug.qss_params['$FieldFormats'])
        self.rows = []
        self.user_data: list[int] = []  # file_id
        self.inserted_row = -1
        ag.signals.cancel_edit.connect(self.edit_cancel)

    def set_inserted_row(self, val: int):
        self.inserted_row = val

    @pyqtSlot()
    def edit_cancel(self):
        try:
            i0 = self.user_data.index(0)
            self.removeRows(i0, 1)
        except ValueError:
            pass
        finally:
            self.inserted_row = -1

    def update_header(self, vals: str):
        def convert_to_str():
            for i in range(len(self.rows)):
                self.rows[i][ii] = ''

        def convert_to_int():
            for i in range(len(self.rows)):
                self.rows[i][ii] = 0

        def convert_to_date():
            for i in range(len(self.rows)):
                self.rows[i][ii] = create_date_obj(ag.ZERO_DATE)

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
                return line[SRT_IDX]
            elif role == SIZE_SORT_ROLE:
                return line[SRT_IDX+1]
            elif role == Qt.ItemDataRole.TextAlignmentRole:
                if col:
                    return Qt.AlignmentFlag.AlignRight
                return Qt.AlignmentFlag.AlignLeft
        return None

    def insertRows(self, row: int, count: int, parent: QModelIndex=QModelIndex()):
        self.beginInsertRows(parent, row, row + count - 1)
        line = [create_date_obj(ag.ZERO_DATE) if x=='date' else 0 if x=='int' else '' for x in self.field_type[1:]]
        for i in range(count):
            self.rows.insert(row, ['<file_name>.md', *line, ('<file_name>','md'), 0])
            self.user_data.insert(row, 0)          # file_id = 0
        self.endInsertRows()
        return True

    def index(self, row, column, parent: QModelIndex=QModelIndex()):
        return self.createIndex(row, column, self.rows[row]) if 0 <= row < len(self.rows) else QModelIndex()

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

        def rename_file(new_name: str) -> bool:
            path = db_ut.get_file_path(file_id)
            new_path = Path(path).parent / new_name
            try:
                Path(path).rename(new_path)
            except (FileExistsError, FileNotFoundError, PermissionError) as e:
                show_message_box('Error renaming file', f'{e}', icon=QStyle.StandardPixmap.SP_MessageBoxCritical)
                return False

            line[0] = new_name
            line[SRT_IDX] = ((new_path.stem.lower(), new_path.suffix.strip('.').lower()) if new_path.suffix else (new_path.stem.lower(),))
            ag.app.ui.current_filename.setText(new_name)
            return True

        def create_file(new_file: str):
            path = tug.get_app_setting('DEFAULT_FILE_PATH', str(Path('~/fileo/files').expanduser()))
            new_path = Path(path) / new_file

            try:
                new_path.touch(exist_ok=False)
            except (FileExistsError, OSError) as e:
                show_message_box('File already exists', f'{e}')
                return

            try:
                cre_time = QDateTime().fromSecsSinceEpoch(int(new_path.stat().st_birthtime))
            except AttributeError:
                cre_time = QDateTime().fromSecsSinceEpoch(int(new_path.stat().st_ctime))

            line[1] = line[5] = line[10] = cre_time
            line[0] = new_file
            line[SRT_IDX] = ((new_path.stem.lower(), new_path.suffix.strip('.').lower()) if new_path.suffix else (new_path.stem.lower(),))
            line[SRT_IDX+1] = 0    # Size

            ff = [line[i].toSecsSinceEpoch() if isinstance(line[i], QDateTime) else line[i] for i in (5,2,10,3,4,7,6,8,1,)]
            file_id, is_new_ext = db_ut.insert_file(('', new_file, *ff[:-1], path), ff[-1], ag.fileSource.CREATED.value)
            self.user_data[row] = file_id
            dir_id = ag.dir_list.currentIndex().data(Qt.ItemDataRole.UserRole).dir_id
            db_ut.copy_file(file_id, dir_id)
            ag.signals.user_signal.emit(f"New file created\\{file_id}")
            if is_new_ext:
                ag.signals.user_signal.emit("ext inserted")

        col = index.column()
        row = index.row()
        file_id = self.user_data[row]
        line = self.rows[row]

        if file_id == 0 and col == 0:
            create_file(value)
            return True
        else:
            field = tug.qss_params['$EditableFields'].get(col, '')
            if field == 'filename':
                if not rename_file(value):
                    return False
            else:
                line[col] = value
                if self.field_type[col] == 'date':
                    value = value.toSecsSinceEpoch()
        db_ut.update_files_field(file_id, field, value)
        self.dataChanged.emit(index, index)
        ag.add_recent_file(self.user_data[index.row()])
        return True

    def get_index_by_id(self, file_id: int) -> QModelIndex:
        try:
            i = self.user_data.index(file_id)
        except ValueError:
            return QModelIndex()
        return self.index(i, 0, QModelIndex())

    def update_opened(self, ts: int, index: QModelIndex):
        """
        ts - the unix epoch timestamp
        """
        row = index.row()
        if "Open#" in self.field_names:
            i = self.field_names.index("Open#")
            self.rows[row][i] += 1
        if "Open Date" in self.field_names:
            i = self.field_names.index("Open Date")
            self.rows[row][i].setSecsSinceEpoch(ts)

    def update_last_note_data(self, val, index: QModelIndex):
        self.rows[index.row()][9] = val

    def fill_model(self, files):
        def append_row():
            self.rows.append(ff1)
            self.user_data.append(ff[-1])   # ff[-1] - file_id

        def field_val():
            if typ == "str":
                return val if val else ''
            if typ == "int":
                try:
                    ret = int(val)
                except ValueError:
                    ret = 0
                return ret
            return create_date_obj(val if isinstance(val, int) else ag.ZERO_DATE)

        sz_val = 0
        for ff in files:
            if not ff[0]:
                continue
            ff1 = []
            for typ, name, val in zip(self.field_type, self.field_names, ff[:-1]):
                if name == 'Size':
                    tt = ag.human_readable_size(val)
                    sz_val = val
                else:
                    tt = field_val()
                ff1.append(tt)

            filename = Path(ff[0])
            ff1.append(             # SRT_IDX
                (filename.stem.lower(), filename.suffix.strip('.').lower())
                if filename.suffix else (filename.stem.lower(),)
            )
            ff1.append(sz_val)      # SRT_IDX+1
            append_row()
