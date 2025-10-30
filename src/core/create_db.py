from loguru import logger
import apsw
from enum import IntEnum

from . import app_globals as ag

DATE_1970_1_1 = ag.DATE_1970_1_1.toSecsSinceEpoch()
APP_ID = 1718185071
USER_VER = 29

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
    # FILENOTES = 10
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
        f'added date not null default {DATE_1970_1_1}, '
        'how_added integer not null, '
        f'modified date not null default {DATE_1970_1_1}, '
        f'opened date not null default {DATE_1970_1_1}, '
        f'created date not null default {DATE_1970_1_1}, '
        'rating integer not null default 0, '
        'nopen integer not null default 0, '
        'hash text, '
        'size integer not null default 0, '
        'pages integer not null default 0, '
        f'published date not null default {DATE_1970_1_1}, '
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
        f'created date not null default {DATE_1970_1_1}, '
        f'modified date not null default {DATE_1970_1_1}, '
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
    except (apsw.CantOpenError, apsw.SQLError, apsw.NotADBError) as e:
        logger.info(f'{e.args}, DB file: {db_path}')
        return e.args[0]

    app_id = conn.cursor().execute("PRAGMA application_id").fetchone()
    return  "Ok" if app_id[0] == APP_ID else "not a fileo database"

def tune_new_version() -> bool:
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
    def update_to_v21():
        try:
            conn.cursor().execute(
                'ALTER TABLE parentdir RENAME COLUMN is_link TO multy;'
            )
        except apsw.SQLError:
            pass

    def update_to_v22():
        sql = (
            "update dirs set multy = 1 where id in ("
            "select id from parentdir p group by id having count(*) > 1)"
        )
        curs = conn.cursor()
        try:
            curs.execute('ALTER TABLE parentdir DROP multy;')
            curs.execute('ALTER TABLE dirs ADD multy integer not null default 0;')
            curs.execute(sql)
        except apsw.SQLError:
            pass

    def update_to_v23():
        sql = 'delete from settings where key = ?'
        conn.cursor().execute(sql, ('DIR_HISTORY',))

    def update_to_v24():
        sql1 = (
            'INSERT or ignore into COPY_FILES select id, extid, '
            f'path, filename, {DATE_1970_1_1}, 1, modified, opened, created, '
            'rating, nopen, hash, size, pages, published FROM files'
        )

        tbl_def = define_tables(tableIdx.FILES).replace("files", "COPY_FILES")
        curs = conn.cursor()
        curs.execute(tbl_def)
        curs.execute(sql1)
        curs.execute('DROP TABLE files')
        curs.execute('ALTER TABLE COPY_FILES RENAME TO files')

    def update_to_v25():
        """
        old format of history: (branches: list, flags: list), curr: int
        new format of history: branches: list, flags: list, curr: int
        """
        hist = ag.get_db_setting('DIR_HISTORY', [])
        logger.info(f'{hist=}')
        if len(hist) == 2:
            h0,h1 = hist
            logger.info(f'{h0=}, {h1=}')
            ag.save_db_settings(DIR_HISTORY=([], [], -1))

    def update_to_v26():
        """
        different path delimiters, "\" and "/" in table "paths"
        change "\" to "/"
        """
        sql = 'update paths set path = REPLACE(path, "\\", "/") where instr(path, "\") > 0'
        conn.cursor().execute(sql).fetchall()

    def update_to_v27():
        def insert_how_added_field():
            sql1 = (
                'INSERT or ignore into COPY_FILES select id, extid, '
                'path, filename, added, 1, modified, opened, created, '
                'rating, nopen, hash, size, pages, published FROM files'
            )
            sql2 = 'update files set how_added = ? where added = created'


            tbl_def = define_tables(tableIdx.FILES).replace("files", "COPY_FILES")
            curs.execute(tbl_def)
            curs.execute(sql1)
            curs.execute('DROP TABLE files')
            curs.execute('ALTER TABLE COPY_FILES RENAME TO files')
            curs.execute(sql2, (ag.fileSource.CREATED.value,))

        def remove_path_duplicates():
            sql1 = (
                "with x(path, min_id, cnt) as ("
                "select path, min(id), count(*) from paths group by path) "
                "update files set path = (select x.min_id from x "
                "join paths p on p.path = x.path "
                "where x.cnt > 1 and files.path = p.id) "
                "where path in ("
                "select p.id from paths p join x on p.path = x.path "
                "where p.id > x.min_id and x.cnt > 1)"
            )
            sql2 = (
                "with x(path, min_id, cnt) as ("
                "select path, min(id), count(*) from paths group by path) "
                "delete from paths where path in ("
                "select path from x where x.cnt > 1 and paths.id > x.min_id)"
            )
            curs.execute(sql1)
            curs.execute(sql2)

        curs = conn.cursor()
        update_to_v26()
        insert_how_added_field()
        remove_path_duplicates()

    def update_to_v28():
        sql = 'SELECT sql FROM sqlite_schema WHERE name = ? and instr(sql, ?);'
        is_ok = conn.cursor().execute(sql, ('settings', 'PRIMARY')).fetchone()
        if not is_ok:
            conn.cursor().execute('DROP TABLE settings')
            conn.cursor().execute(define_tables(tableIdx.SETTINGS))

    def update_to_v29():
        to_upd = (('files', 'added'), ('files',  'modified'),
                  ('files',  'opened'), ('files',  'created'), ('files',  'published'),
                  ('filenotes', 'created'), ('filenotes', 'modified'))
        def update_min_date():
            sql = f'update {tbl} set {fld} = {DATE_1970_1_1} where {fld} < -86400;'
            curs.execute(sql)

        curs = conn.cursor()
        for tbl,fld in to_upd:
            update_min_date()

    if db_v < 21:
        update_to_v21()

    if db_v < 22:
        update_to_v22()

    if db_v < 23:
        update_to_v23()

    if db_v < 24:
        update_to_v24()

    if db_v < 25:
        update_to_v25()

    if db_v < 26:
        update_to_v26()

    if db_v < 27:
        update_to_v27()

    if db_v < 28:
        update_to_v28()

    if db_v < 29:
        update_to_v29()

    conn.cursor().execute(f'PRAGMA user_version={USER_VER}')

def create_tables(db_name: str):
    conn = apsw.Connection(db_name)
    conn.cursor().execute('pragma journal_mode=WAL')
    conn.cursor().execute(f'PRAGMA application_id={APP_ID}')
    conn.cursor().execute(define_tables())
    conn.cursor().execute(f'PRAGMA user_version={USER_VER}')
