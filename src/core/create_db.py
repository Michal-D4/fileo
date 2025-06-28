import apsw
from loguru import logger

from . import app_globals as ag

TABLES = (
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
    'added date not null default -62135596800, '
    'modified date not null default -62135596800, '
    'opened date not null default -62135596800, '
    'created date not null default -62135596800, '
    'rating integer not null default 0, '
    'nopen integer not null default 0, '
    'hash text, '
    'size integer not null default 0, '
    'pages integer not null default 0, '
    'published date not null default -62135596800, '
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
    'created date not null default -62135596800, '
    'modified date not null default -62135596800, '
    'PRIMARY KEY(fileid, id), '
    'FOREIGN KEY (fileid) REFERENCES files (id) on delete cascade); '
    ),
    (                # extensions
    'CREATE TABLE IF NOT EXISTS extensions ('
    'id integer PRIMARY KEY NOT NULL, '
    'extension text); '
    ),
)

APP_ID = 1718185071
USER_VER = 25

def check_app_schema(db_name: str) -> bool:
    with apsw.Connection(db_name) as conn:
        try:
            v = conn.cursor().execute("PRAGMA application_id").fetchone()
            # logger.info(f'{v=}, {APP_ID=}')
        except apsw.NotADBError:
            return False
    return v[0] == APP_ID

def tune_new_version() -> bool:
    conn = ag.db.conn
    try:
        v = conn.cursor().execute("PRAGMA user_version").fetchone()
        logger.info(f'{v=}, {USER_VER=}')
        if v[0] != USER_VER:
            convert_to_new_version(conn, v[0])
    except apsw.SQLError as err:
        logger.exception(f'{err.args}', exc_info=True)
        return False
    return True

def convert_to_new_version(conn, db_v):
    logger.info(f'<<<  {db_v=}, {USER_VER=}')

    if db_v < 21:
        update_to_v21(conn)

    if db_v < 22:
        update_to_v22(conn)

    if db_v < 23:
        update_to_v23(conn)

    if db_v < 24:
        update_to_v24(conn)

    if db_v < 25:
        update_to_v25()

    conn.cursor().execute(f'PRAGMA user_version={USER_VER}')

def update_to_v21(conn: apsw.Connection):
    try:
        conn.cursor().execute(
            'ALTER TABLE parentdir RENAME COLUMN is_link TO multy;'
        )
    except apsw.SQLError:
        pass

def update_to_v22(conn: apsw.Connection):
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

def update_to_v23(conn: apsw.Connection):
    sql = 'delete from settings where key = ?'
    conn.cursor().execute(sql, ('DIR_HISTORY',))

def update_to_v24(conn: apsw.Connection):
    sql1 = (
        'INSERT or ignore into COPY_FILES select id, extid, '
        'path, filename, -62135596800, modified, opened, created, '
        'rating, nopen, hash, size, pages, published FROM files'
    )

    tbl_def = TABLES[1].replace("files", "COPY_FILES")
    curs = conn.cursor()
    curs.execute(tbl_def)
    curs.execute(sql1)
    curs.execute('DROP TABLE files')
    curs.execute('ALTER TABLE COPY_FILES RENAME TO files')

def update_to_v25():
    hist = ag.get_db_setting('DIR_HISTORY', [])
    logger.info(f'{hist=}')
    if len(hist) == 2:
        h0,h1 = hist
        logger.info(f'{h0=}, {h1=}')
        ag.save_db_settings(DIR_HISTORY=(*h0, h1))

def create_tables(db_name: str):
    conn = apsw.Connection(db_name)
    conn.cursor().execute('pragma journal_mode=WAL')
    conn.cursor().execute(f'PRAGMA application_id={APP_ID}')
    cursor = conn.cursor()
    for tbl in TABLES:
        cursor.execute(tbl)

    conn.cursor().execute(f'PRAGMA user_version={USER_VER}')
