from loguru import logger
import apsw
from enum import IntEnum

from PyQt6.QtCore import QSettings

from . import app_globals as ag
from .. import tug

APP_ID = 1718185071
USER_VER = 31

class tableIdx(IntEnum):
    SETTINGS = 0
    FILES = 1
    # DIRS = 2
    # PATHS = 3
    # FILEDIR = 4
    # PARENTDIR = 5
    # TAGS = 6
    # FILETAG = 7
    # AUTHORS = 8
    # FILEAUTHOR = 9
    FILENOTES = 10
    # EXTENSIONS = 11


def define_tables(idx: int|None = None):
    tables = (
        (                # settings
        'CREATE TABLE IF NOT EXISTS settings ('
        'key text PRIMARY KEY NOT NULL, '
        'value blob); '
        ),
        (                # files
        'CREATE TABLE IF NOT EXISTS files ('
        'id integer PRIMARY KEY NOT NULL, '
        'extid integer NOT NULL, '
        'path integer NOT NULL, '
        'filename text NOT NULL, '
        'added date not null, '
        'how_added integer not null, '
        'modified date not null, '
        'opened date not null, '
        'created date not null, '
        'rating integer not null default 0, '
        'nopen integer not null default 0, '
        'hash text, '
        'size integer not null default 0, '
        'pages integer not null default 0, '
        'published date, '
        'FOREIGN KEY (extid) REFERENCES extensions (id)); '
        ),
        (                # dirs
        'CREATE TABLE IF NOT EXISTS dirs ('
        'id integer PRIMARY KEY NOT NULL, '
        'name text, '
        'multy integer not null default 0); '
        ),
        (                # paths
        'CREATE TABLE IF NOT EXISTS paths ('
        'id integer PRIMARY KEY NOT NULL, '
        'path text); '
        ),
        (                # filedir
        'CREATE TABLE IF NOT EXISTS filedir ('
        'file integer NOT NULL, '
        'dir integer NOT NULL, '
        'PRIMARY KEY(dir, file), '
        'FOREIGN KEY (dir) REFERENCES dirs (id) on delete cascade, '
        'FOREIGN KEY (file) REFERENCES files (id) on delete cascade); '
        ),
        (                # parentdir
        'CREATE TABLE IF NOT EXISTS parentdir ('
        'parent integer NOT NULL, '
        'id integer NOT NULL, '
        'hide integer not null default 0, '
        'file_id integer not null default 0, '
        'tool_tip text, '
        'PRIMARY KEY(parent, id)); '
        ),
        (                # tags
        'CREATE TABLE IF NOT EXISTS tags ('
        'id integer PRIMARY KEY NOT NULL, '
        'tag text NOT NULL); '
        ),
        (                # filetag
        'CREATE TABLE IF NOT EXISTS filetag ('
        'fileid integer NOT NULL, '
        'tagid integer NOT NULL, '
        'PRIMARY KEY(fileid, tagid), '
        'FOREIGN KEY (fileid) REFERENCES files (id) on delete cascade, '
        'FOREIGN KEY (tagid) REFERENCES tags (id) on delete cascade); '
        ),
        (                # authors
        'CREATE TABLE IF NOT EXISTS authors ('
        'id integer PRIMARY KEY NOT NULL, '
        'author text NOT NULL); '
        ),
        (                # fileauthor
        'CREATE TABLE IF NOT EXISTS fileauthor ('
        'fileid integer NOT NULL, '
        'aid integer NOT NULL, '
        'PRIMARY KEY(fileid, aid), '
        'FOREIGN KEY (aid) REFERENCES authors (id) on delete cascade, '
        'FOREIGN KEY (fileid) REFERENCES files (id) on delete cascade); '
        ),
        (                # filenotes
        'CREATE TABLE IF NOT EXISTS filenotes ('
        'fileid integer NOT NULL, '
        'id integer NOT NULL, '
        'filenote text NOT NULL, '
        'created date not null, '
        'modified date not null, '
        'PRIMARY KEY(fileid, id), '
        'FOREIGN KEY (fileid) REFERENCES files (id) on delete cascade); '
        ),
        (                # extensions
        'CREATE TABLE IF NOT EXISTS extensions ('
        'id integer PRIMARY KEY NOT NULL, '
        'extension text); '
        ),
    )
    return ''.join(tables) if idx is None else tables[idx]

def check_app_schema(db_path: str) -> str:
    try:
        conn = apsw.Connection(db_path)
        conn.cursor().execute('PRAGMA quick_check;').fetchone()
    except (apsw.CantOpenError, apsw.SQLError, apsw.NotADBError, apsw.BusyError) as e:
        logger.info(f'{e.args}, DB file: {db_path}')
        return e.args[0]

    app_id = conn.cursor().execute("PRAGMA application_id").fetchone()
    return  "Ok" if app_id[0] == APP_ID else "not a fileo database"

def clean_app_settings(cur_v: int):
    app_params = tug.qss_params["@appSettings"]
    upd = tug.qss_params["@appSettingsUpd"]
    app_par_set = set(app_params)-set(upd)
    settings = QSettings(tug.MAKER, tug.APP_NAME)
    for key in settings.allKeys():
        if key in app_par_set:
            continue
        settings.remove(key)
    tug.save_app_setting(AppVersion=cur_v)

def clean_db_settings(cur_v: int):
    i = tug.qss_params["$FileListFields"].index("Recent")
    old_type = ag.get_db_setting("FieldTypes", tug.qss_params["$FieldTypes"])[i]
    conn = ag.db.conn
    if old_type != 'date':
        conn.cursor().execute('update files set published = opened')

    db_params = tug.qss_params["@dbSettings"]
    upd = tug.qss_params["@dbSettingsUpd"]
    db_par_set = set(db_params)-set(upd)
    for key in conn.cursor().execute('select key from settings'):
        if key[0] in db_par_set:
            continue
        conn.cursor().execute('delete from settings where key = ?', key)
    ag.save_db_settings(AppVersion=cur_v)

def tune_new_version() -> bool:
    cur_v = int(ag.app_version().replace('.', ''))
    stored_v = tug.get_app_setting("AppVersion", cur_v)
    if isinstance(stored_v, str):
        stored_v = int(stored_v.replace('.', ''))
    logger.info(f'{cur_v=}, {stored_v=}')
    if cur_v != stored_v:
        clean_app_settings(cur_v)

    stored_v = ag.get_db_setting("AppVersion", cur_v)
    if isinstance(stored_v, str):
        stored_v = int(stored_v.replace('.', ''))
    logger.info(f'{cur_v=}, {stored_v=}')
    if cur_v != stored_v:
        clean_db_settings(cur_v)

    conn = ag.db.conn
    try:
        v = conn.cursor().execute("PRAGMA user_version").fetchone()
        logger.info(f'{v=}, {USER_VER=}')
        if v[0] < USER_VER:
            convert_to_new_version(conn, v[0])
    except apsw.SQLError as err:
        logger.exception(f'{err.args}', exc_info=True)
        return False
    return True

def convert_to_new_version(conn, db_v):
    logger.info(f'<<<  {db_v=}, {USER_VER=}, {ag.db.path=}')
    def update_to_v30(names):
        def drop_old_tbl(table: str):
            curs.execute(f'DROP TABLE {table}')
            curs.execute(f'ALTER TABLE COPY_{table} RENAME TO {table}')
        for tbl_id, name in names.items():
            copy_tbl(tbl_id, name)
            drop_old_tbl(name)

    def copy_tbl(tbl_id: int, table: str):
        sql = f'INSERT or ignore into COPY_{table} select * FROM {table}'
        tbl_def = define_tables(tbl_id).replace(table, f"COPY_{table}")
        curs.execute(tbl_def)
        curs.execute(sql)

    curs = conn.cursor()

    if db_v < 30:
        update_to_v30({tableIdx.FILES: "files",  tableIdx.FILENOTES: "filenotes"})

    if db_v < 31:
        update_to_v30({tableIdx.FILES: "files",})

    conn.cursor().execute(f'PRAGMA user_version={USER_VER}')

def create_tables(db_name: str):
    conn = apsw.Connection(db_name)
    conn.cursor().execute('pragma journal_mode=WAL')
    conn.cursor().execute(f'PRAGMA application_id={APP_ID}')
    conn.cursor().execute(define_tables())
    conn.cursor().execute(f'PRAGMA user_version={USER_VER}')
