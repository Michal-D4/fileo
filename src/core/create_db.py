import apsw
from loguru import logger

from . import app_globals as ag

TABLES = (
    (
    'CREATE TABLE IF NOT EXISTS settings ('
    'key text NOT NULL, '
    'value blob); '
    ),
    (
    'CREATE TABLE IF NOT EXISTS files ('
    'id integer PRIMARY KEY NOT NULL, '
    'extid integer NOT NULL, '
    'path integer NOT NULL, '
    'filename text NOT NULL, '
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
    (
    'CREATE TABLE IF NOT EXISTS dirs ('
    'id integer PRIMARY KEY NOT NULL, '
    'name text); '
    ),
    (
    'CREATE TABLE IF NOT EXISTS paths ('
    'id integer PRIMARY KEY NOT NULL, '
    'path text); '
    ),
    (
    'CREATE TABLE IF NOT EXISTS filedir ('
    'file integer NOT NULL, '
    'dir integer NOT NULL, '
    'PRIMARY KEY(dir, file), '
    'FOREIGN KEY (dir) REFERENCES dirs (id) on delete cascade, '
    'FOREIGN KEY (file) REFERENCES files (id) on delete cascade); '
    ),
    (
    'CREATE TABLE IF NOT EXISTS parentdir ('
    'parent integer NOT NULL, '
    'id integer NOT NULL, '
    'is_link integer not null default 0, '
    'hide integer not null default 0, '
    'file_id integer not null default 0, '
    'PRIMARY KEY(parent, id)); '
    ),
    (
    'CREATE TABLE IF NOT EXISTS tags ('
    'id integer PRIMARY KEY NOT NULL, '
    'tag text NOT NULL); '
    ),
    (
    'CREATE TABLE IF NOT EXISTS filetag ('
    'fileid integer NOT NULL, '
    'tagid integer NOT NULL, '
    'PRIMARY KEY(fileid, tagid), '
    'FOREIGN KEY (fileid) REFERENCES files (id) on delete cascade, '
    'FOREIGN KEY (tagid) REFERENCES tags (id) on delete cascade); '
    ),
    (
    'CREATE TABLE IF NOT EXISTS authors ('
    'id integer PRIMARY KEY NOT NULL, '
    'author text NOT NULL); '
    ),
    (
    'CREATE TABLE IF NOT EXISTS fileauthor ('
    'fileid integer NOT NULL, '
    'aid integer NOT NULL, '
    'PRIMARY KEY(fileid, aid), '
    'FOREIGN KEY (aid) REFERENCES authors (id) on delete cascade, '
    'FOREIGN KEY (fileid) REFERENCES files (id) on delete cascade); '
    ),
    (
    'CREATE TABLE IF NOT EXISTS filenotes ('
    'fileid integer NOT NULL, '
    'id integer NOT NULL, '
    'filenote text NOT NULL, '
    'created date not null default -62135596800, '
    'modified date not null default -62135596800, '
    'PRIMARY KEY(fileid, id), '
    'FOREIGN KEY (fileid) REFERENCES files (id) on delete cascade); '
    ),
    (
    'CREATE TABLE IF NOT EXISTS extensions ('
    'id integer PRIMARY KEY NOT NULL, '
    'extension text); '
    ),
)
APP_ID = 1718185071
USER_VER = 8

def check_app_schema(db_name: str) -> bool:
    with apsw.Connection(db_name) as conn:
        try:
            v = conn.cursor().execute("PRAGMA application_id").fetchone()
        except apsw.NotADBError:
            return False
    return v[0] == APP_ID

def tune_new_version() -> bool:
    conn = ag.db['Conn']
    try:
        v = conn.cursor().execute("PRAGMA user_version").fetchone()

        if v[0] != USER_VER:
            v[0] = convert_to_new_version(conn, v[0])
    except apsw.SQLError as err:
        logger.info(err)
        return False

    tune_app_version(conn)

    return v[0] == USER_VER

def convert_to_new_version(conn, old_v) -> int:
    if old_v == 0:
        create_tables(conn)
        return USER_VER

def create_db(db_name: str) -> apsw.Connection:
    return apsw.Connection(db_name)

def create_tables(conn: apsw.Connection):
    conn.cursor().execute('pragma journal_mode=WAL')
    conn.cursor().execute(f'PRAGMA application_id={APP_ID}')
    conn.cursor().execute(f'PRAGMA user_version={USER_VER}')
    cursor = conn.cursor()
    for tbl in TABLES:
        cursor.execute(tbl)

    initiate_db(conn)

def initialize_settings(connection):
    sql = (
        'insert into settings (key) select (:key) '
        'where not exists (select key from settings '
        'where key = :key)'
    )
    cursor = connection.cursor()
    for name in ag.setting_names:
        cursor.execute(sql, {'key': name})

    save_version(connection)

def save_version(connection):
    ag.save_settings(APP_VERSION=ag.app_version())

def tune_app_version(conn: apsw.Connection):
    curr_ver = ag.get_setting('APP_VERSION', '')
    new_ver = ag.app_version()
    if curr_ver != new_ver:
        save_version(conn)

def initiate_db(connection):
    sql = (
        'insert or ignore into dirs (id) values (:key)',
        'insert or ignore into dirs values (:key, :val)',
    )
    curs = connection.cursor()
    curs.execute(sql[0], {'key': 0})
    curs.execute(sql[1], {'key': 1, 'val': '@@Lost'})

    initialize_settings(connection)
