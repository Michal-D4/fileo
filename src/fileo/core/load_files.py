from loguru import logger
import apsw
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

    def __init__(self, root: str, ext: list[str], parent = None) -> None:
        super().__init__(parent)

        self.root: str = root
        self.ext: list[str] = ext
        self.paths: dict[PathDir] = {}
        self.ext_inserted = False

        self.conn = apsw.Connection(ag.db['Path'])
        self.init_path()

    def init_path(self):
        sql = 'select * from paths'
        cursor = self.conn.cursor().execute(sql)
        for row in cursor:
            if Path(row[-1]).is_dir():  # skip not dirs
                self.paths[row[-1]] = PathDir(row[0], 0)

    def load_data(self):
        """
        Load data in data base
        :param data: - iterable lines of file names with full path
        :return: None
        """
        if self.root not in self.paths:
            dir_id, path_id = self.insert_dir(Path(self.root))
            self.paths[self.root] = PathDir(path_id, dir_id)

        files = yield_files(self.root, self.ext)
        for line in files:
            if ag.stop_thread:
                break
            file = Path(line)
            file_path = file.parent
            dir_id, path_id = self.insert_dir(file_path)
            if dir_id > 0:
                self.insert_file(dir_id, path_id, file)

        self.conn.close()
        self.finished.emit(self.ext_inserted)

    def insert_file(self, dir_id: int, path_id: int, full_file_name: Path):
        """
        Insert file into Files table
        :param dir_id: int > 0
        :param full_file_name:
        :return: None
        """
        FIND_FILE = ('select id from files where path = :pid and filename = :name')
        INSERT_FILE = ('insert into files (filename, extid, path) '
            'values (:file, :ext_id, :path);')
        INSERT_FILEDIR = 'insert into filedir values (:file, :dir);'

        file_name = full_file_name.name
        path = full_file_name.parent

        cursor = self.conn.cursor()
        id_found = cursor.execute(
            FIND_FILE, {'pid': self.paths[str(path)].pathId, 'name': file_name}).fetchone()
        if not id_found:
            ext_id = self.insert_extension(full_file_name)
            cursor.execute(INSERT_FILE, {'file': file_name,
                                         'ext_id': ext_id,
                                         'path': path_id})
            id = self.conn.last_insert_rowid()
            cursor.execute(INSERT_FILEDIR, {'file': id, 'dir': dir_id})

    def insert_extension(self, file: Path) -> int:
        """
        insert or find extension in DB
        :param file - file name
        returns (ext_id, extension_of_file)
        """
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

    def insert_dir(self, new_path: Path) -> tuple[int, int]:
        """
        Insert file path into Dirs table if not exist yet
        :param new_path: path of picked file
        :return: id_dir, id_path  of new_path
        """
        p_id, path_id, parent_path = self.find_closest_parent(new_path)

        # is the closest parent equal to new_path ?
        if parent_path and parent_path.samefile(new_path):
            return p_id, path_id      # p_id is id of new_path dir here

        id_dir, id_path = self._insert_dir(p_id, new_path)

        self.change_parent(id_dir, p_id, new_path)

        self.paths[str(new_path)] = PathDir(id_path, id_dir)

        return id_dir, id_path

    def _insert_dir(self, parent: int, new_path: Path) -> tuple[int, int]:
        INSERT_DIR = 'insert into dirs (name) values (:name)'
        INSERT_PATH = 'insert into paths (path) values (:path)'
        INSERT_PARENT = 'insert into parentdir (parent, id) values (:p_id, :id)'

        cursor = self.conn.cursor()

        cursor.execute(INSERT_DIR, {'name': new_path.name})
        id_dir = self.conn.last_insert_rowid()

        cursor.execute(INSERT_PATH, {'path': str(new_path)})
        id_path = self.conn.last_insert_rowid()

        cursor.execute(INSERT_PARENT, {'p_id': parent, 'id': id_dir})

        return id_dir, id_path

    def change_parent(self, id: int, p_id: int, path: Path):
        """
        Change parent id of dirs that must be children of new dir
        :param id: id of new dir
        :param p_id: parent id of new dir
        :param path: path of new dir
        """
        UPDATE_PARENT = (
            'update PARENTDIR set parent = :new_id '
            'where id = :dir and parent = :old_id'
        )

        cursor = self.conn.cursor()
        for key, it in self.paths.items():
            if Path(key) in path.parents and it.dirId != id:
                cursor.execute(UPDATE_PARENT,
                    {'dir': it.dirId, 'old_id': p_id, 'new_id': id}
                )

    def find_closest_parent(self, new_path: Path) -> tuple[int, int, Path]:
        """
        Search parent directory in DB
        :param new_path:  new file path
        :return: parent_id, path_id, parent_path
             or  0,         0,       None
        """
        # WORKAROUND: the dummy path "path / '@'" uses
        # to include the new_path into considered parents
        for prnt_path in (new_path / '@').parents:
            str_prnt = str(prnt_path)
            if str_prnt in self.paths:
                item: PathDir = self.paths[str_prnt]
                path_id = item.pathId
                prnt_id = item.dirId or path_id
                self.parent_dir_id(prnt_id, prnt_path.name)
                return prnt_id, path_id, prnt_path

        return 0, 0, None

    def parent_dir_id(self, prnt_id: int, prnt: str):
        """
        be sure that dir with id=path_id exist in dirs table
        """
        IS_PARENT_IN_DIRS = 'select 1 from dirs where id = :parent'
        INSERT_PARENT = 'insert into dirs (id, name) values (:id, :name)'
        SET_PARENT_ROOT = 'insert into parentdir (parent, id) values (0, :id);'

        cursor = self.conn.cursor()
        res = cursor.execute(IS_PARENT_IN_DIRS, {'parent': prnt_id}).fetchone()
        if not res:   # parent_id doesn't exist in dirs, creating:
            cursor.execute(INSERT_PARENT, {'id': prnt_id, 'name': prnt})
            cursor.execute(SET_PARENT_ROOT, {'id': prnt_id})
