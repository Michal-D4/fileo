# from loguru import logger
import apsw
from datetime import datetime
from dataclasses import dataclass
from pathlib import Path
from PyQt6.QtCore import pyqtSignal, QObject, pyqtSlot

from . import app_globals as ag

@dataclass(slots=True)
class PathDir():
    pathId: int
    dirId: int

def yield_files(root: str, ext: list[str]):
    """
    generator of file list
    :param root: root directory
    :param ext: list of extensions
    """
    r_path = Path(root)
    for filepath in r_path.rglob('*'):
        if not filepath.is_file():
            continue
        if '*' in ext:
            yield filepath
        elif filepath.suffix.strip('.') in ext:
            yield filepath


class loadFiles(QObject):
    finished = pyqtSignal(bool)

    def __init__(self, parent = None) -> None:
        super().__init__(parent)

        self.root_id = 0
        self.dir_id = 0
        self.paths: dict[PathDir] = {}
        self.ext_inserted = False
        self.files = None

        self.conn = apsw.Connection(ag.db.path)
        self.init_path()

    def init_path(self):
        sql = 'select * from paths'
        cursor = self.conn.cursor().execute(sql)
        for row in cursor:
            if Path(row[-1]).is_dir():  # changes in os file system may happened, and registered dir removed
                self.paths[row[-1]] = PathDir(row[0], 0)

    def set_files_iterator(self, files):
        """
        files should be iterable
        I do not check if it is iterable
        there is no simple way to check
        only try to use
        """
        self.files = files

    def load_to_dir(self, dir_id):
        def drop_file():
            if not file.is_file():
                return
            path_id = self.get_path_id(file.parent.as_posix())

            self._insert_file(path_id, file, ag.fileSource.DRAG_SYS.value, dragged_ts)

        dragged_ts = int(datetime.now().replace(microsecond=0).timestamp())
        self.dir_id = dir_id
        for line in self.files:
            file = Path(line)
            drop_file()

        if self.ext_inserted:
            ag.signals.user_signal.emit("ext inserted")
        self.conn.close()

    @pyqtSlot()
    def load_data(self):
        """
        Load data in data base
        :param data: - iterable lines of file names with full path
        :return: None
        abend happen if self.files is not iterable
        """
        def create_load_dir():
            load_dir = f'Load {datetime.now().strftime("%b %d %H:%M")}'
            self.root_id = self._insert_dir(load_dir)
            self.add_parent_dir(0, self.root_id)

        def insert_file():
            """
            :param full_file_name:
            :return: file_id if inserted new, 0 if already exists
            """
            path_id = self.get_path_id(file.parent.as_posix())

            self.dir_id = self.get_dir_id(file.parent, path_id)

            self._insert_file(path_id, file, ag.fileSource.SCAN_SYS.value, add_ts)

        create_load_dir()

        add_ts = int(datetime.now().replace(microsecond=0).timestamp())

        for line in self.files:
            if ag.stop_thread:
                break

            file = Path(line)
            insert_file()
        self.conn.close()
        self.finished.emit(self.ext_inserted)

    def _insert_file(self, path_id: int, filepath: Path, source: int, add_time: int):
        def insert_extension() -> int:
            FIND_EXT = 'select id from extensions where lower(extension) = ?;'
            INSERT_EXT = 'insert into extensions (extension) values (:ext);'

            ext = filepath.suffix.strip('.')
            cursor = self.conn.cursor()
            item = cursor.execute(FIND_EXT, (ext.lower(),)).fetchone()
            if item:
                return item[0]

            cursor.execute(INSERT_EXT, {'ext': ext})
            self.ext_inserted = True
            return self.conn.last_insert_rowid()

        def find_file() -> int:
            FIND_FILE = ('select id from files where path = :pid and filename = :name')
            file_id = self.conn.cursor().execute(FIND_FILE,
                {'pid': path_id, 'name': filepath.name}
            ).fetchone()
            return file_id[0] if file_id else 0

        def file_insert() -> int:
            INSERT_FILE = ('insert into files (filename, extid, path, added, how_added) '
                'values (:file, :ext_id, :path, :added, :how);')
            self.conn.cursor().execute(INSERT_FILE,
                {'file': filepath.name, 'ext_id': ext_id, 'path': path_id, 'added': add_time, 'how': source}
            )
            return self.conn.last_insert_rowid()

        def set_file_dir_link():
            INSERT_FILEDIR = 'insert into filedir values (:file, :dir);'
            try:
                self.conn.cursor().execute(
                    INSERT_FILEDIR, {'file': file_id, 'dir': self.dir_id}
                )
            except apsw.ConstraintError:
                pass

        ext_id = insert_extension()

        file_id = find_file() or file_insert()

        set_file_dir_link()

    def get_dir_id(self, path: Path, path_id: int) -> int:
        str_path = path.as_posix()
        if str_path in self.paths:
            dir_id = self.paths[str_path].dirId
            if dir_id:
                return dir_id

        parent_id = self.find_closest_parent(path)
        dir_id = self._new_dir(path, parent_id)
        self.paths[str_path] = PathDir(path_id, dir_id)
        return dir_id

    def _new_dir(self, path: Path, parent_id: int) -> int:
        dir_id = self._insert_dir(path.name)
        self.add_parent_dir(parent_id, dir_id)
        return dir_id

    def _insert_dir(self, dir_name: str) -> int:
        INSERT_DIR = 'insert into dirs (name) values (:name)'

        self.conn.cursor().execute(INSERT_DIR, {'name': dir_name})
        dir_id = self.conn.last_insert_rowid()

        return dir_id

    def get_path_id(self, path: str) -> int:
        if path in self.paths:
            return self.paths[path].pathId

        INSERT_PATH = 'insert into paths (path) values (:path)'
        self.conn.cursor().execute(INSERT_PATH, {'path': path})
        path_id = self.conn.last_insert_rowid()
        self.paths[path] = PathDir(path_id, 0)
        return path_id

    def add_parent_dir(self, parent: int, id_dir: int):
        INSERT_PARENT = (
            'insert into parentdir (parent, id) '
            'values (:p_id, :id)'
        )

        self.conn.cursor().execute(
            INSERT_PARENT, {'p_id': parent, 'id': id_dir}
        )

    def find_closest_parent(self, new_path: Path) -> int:
        """
        Search parent directory in DB
        :param new_path:  new file path
        :return: parent_id, parent_path
             or  0,         None
        """
        # the first parent of "new_path / '@'" is a new_path itself
        for parent_path in (new_path / '@').parents:
            str_parent = parent_path.as_posix()
            if str_parent in self.paths:
                return self.paths[str_parent].dirId or self.root_id

        return self.root_id
