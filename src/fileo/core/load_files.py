from loguru import logger
import apsw
from datetime import datetime
from dataclasses import dataclass
from pathlib import Path
from PyQt6.QtCore import pyqtSignal, QObject

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
    for filename in r_path.rglob('*'):
        if not filename.is_file():
            continue
        if '*' in ext:
            yield filename
        elif filename.suffix.strip('.') in ext:
            yield filename


class loadFiles(QObject):
    finished = pyqtSignal(bool)

    def __init__(self, parent = None) -> None:
        super().__init__(parent)

        self.load_id = 0
        self.paths: dict[PathDir] = {}
        self.ext_inserted = False
        self.files = None

        self.conn = apsw.Connection(ag.db['Path'])
        self.init_path()

    def init_path(self):
        sql = 'select * from paths'
        cursor = self.conn.cursor().execute(sql)
        for row in cursor:
            if Path(row[-1]).is_dir():  # skip not dirs
                logger.info(f"Path: {row[-1]}, pathId: {row}")
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
        self.load_id = dir_id
        logger.info(f"{self.load_id=}")
        for line in self.files:
            logger.info(line)
            file = Path(line)
            self.drop_file(file)

        self.conn.close()

    def drop_file(self, filename: Path):
        path_id = self.get_path_id(str(filename.parent))

        logger.info(f'{path_id=}, {filename}')
        id = (
            self.find_file(path_id, filename.name) or
            self._drop_file(path_id, filename)
        )

        logger.info(f"{id=}, {self.load_id=}")
        self.set_file_dir_link(id, self.load_id)

    def _drop_file(self, path_id: int, file_name: Path) -> int:
        INSERT_FILE = ('insert into files (filename, extid, path) '
            'values (:file, :ext_id, :path);')

        ext_id = self.insert_extension(file_name)

        logger.info(f"{ext_id=}, {path_id=}, {file_name.name}")
        self.conn.cursor().execute(INSERT_FILE,
            {'file': file_name.name, 'ext_id': ext_id, 'path': path_id}
        )
        return self.conn.last_insert_rowid()

    def load_data(self):
        """
        Load data in data base
        :param data: - iterable lines of file names with full path
        :return: None
        abend happen if self.files is not iterable
        """
        self.create_load_dir()

        for line in self.files:
            if ag.stop_thread:
                break

            file = Path(line)
            id = self.insert_file(file)
            logger.info(f"{id=}")

        self.conn.close()
        self.finished.emit(self.ext_inserted)

    def create_load_dir(self):
        load_dir = f'Load {datetime.now().strftime("%b %d %H:%M")}'
        self.load_id = self._insert_dir(load_dir)
        logger.info(f'{self.load_id=}')
        self.add_parent_dir(0, self.load_id)

    def insert_file(self, full_file_name: Path) -> int:
        """
        Insert file into files table
        :param full_file_name:
        :return: file_id if inserted new, 0 if already exists
        """
        path_id = self.get_path_id(str(full_file_name.parent))

        logger.info(f"{path_id=}, {str(full_file_name)}")

        if self.find_file(path_id, full_file_name.name):
            return 0

        return self._insert_file(path_id, full_file_name)

    def _insert_file(self, path_id: int, file_name: Path):
        INSERT_FILE = ('insert into files (filename, extid, path) '
            'values (:file, :ext_id, :path);')

        dir_id = self.get_dir_id(file_name.parent, path_id)

        ext_id = self.insert_extension(file_name)

        self.conn.cursor().execute(INSERT_FILE,
            {'file': file_name.name, 'ext_id': ext_id, 'path': path_id}
        )
        id = self.conn.last_insert_rowid()

        self.set_file_dir_link(id, dir_id)
        return id

    def set_file_dir_link(self, id: int, dir_id: int):
        INSERT_FILEDIR = 'insert into filedir values (:file, :dir);'
        logger.info(f'{id=}, {dir_id=}')
        self.conn.cursor().execute(INSERT_FILEDIR, {'file': id, 'dir': dir_id})

    def find_file(self, path_id: int, file_name: str) -> int:
        FIND_FILE = ('select id from files where path = :pid and filename = :name')

        logger.info(f'{path_id=}, {file_name}')
        id = self.conn.cursor().execute(FIND_FILE,
            {'pid': path_id, 'name': file_name}
        ).fetchone()

        return id[0] if id else 0

    def get_dir_id(self, path: Path, path_id: int) -> int:
        if str(path) in self.paths:
            logger.info(f'{self.paths[str(path)]}, {str(path)}')
            id = self.paths[str(path)].dirId
            if id:
                return id

        parent_id = self.find_closest_parent(path)
        id = self._new_dir(path, parent_id)
        self.paths[str(path)] = PathDir(path_id, id)
        logger.info(f'{self.paths[str(path)]}, {str(path)}')
        return id

    def _new_dir(self, path: Path, parent_id: int):
        id = self._insert_dir(path.name)
        logger.info(f'{id=}, {parent_id=}')
        self.add_parent_dir(parent_id, id)
        return id

    def _insert_dir(self, dir_name: str) -> int:
        INSERT_DIR = 'insert into dirs (name) values (:name)'

        self.conn.cursor().execute(INSERT_DIR, {'name': dir_name})
        id_dir = self.conn.last_insert_rowid()

        return id_dir

    def get_path_id(self, path: str) -> int:
        INSERT_PATH = 'insert into paths (path) values (:path)'

        if path in self.paths:
            return self.paths[path].pathId

        self.conn.cursor().execute(INSERT_PATH, {'path': path})
        path_id = self.conn.last_insert_rowid()
        self.paths[path] = PathDir(path_id, 0)
        return path_id

    def insert_extension(self, file: Path) -> int:
        FIND_EXT = 'select id from extensions where extension = ?;'
        INSERT_EXT = 'insert into extensions (extension) values (:ext);'

        ext = file.suffix.strip('.')
        cursor = self.conn.cursor()
        item = cursor.execute(FIND_EXT, (ext,)).fetchone()
        if item:
            return item[0]

        cursor.execute(INSERT_EXT, {'ext': ext})
        self.ext_inserted = True
        return self.conn.last_insert_rowid()

    def add_parent_dir(self, parent: int, id_dir: int):
        INSERT_PARENT = (
            'insert into parentdir (parent, id) '
            'values (:p_id, :id)'
        )

        logger.info(f'{parent=}, {id_dir=}')
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
        logger.info(f"{str(new_path)=}")
        for parent_path in (new_path / '@').parents:
            str_parent = str(parent_path)
            logger.info(f'parent:{str_parent}')
            if str_parent in self.paths:
                return self.paths[str_parent].dirId or self.load_id

        return self.load_id
