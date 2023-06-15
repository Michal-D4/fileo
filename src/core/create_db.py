import apsw
from loguru import logger

from . import app_globals as ag

TABLES = (
"""
CREATE TABLE settings (
key text NOT NULL,
value blob
);
""",
"""
CREATE TABLE files (
id integer PRIMARY KEY NOT NULL,
extid integer NOT NULL,
path integer NOT NULL,
filename text NOT NULL,
modified date not null default -62135596800,
opened date not null default -62135596800,
created date not null default -62135596800,
rating integer not null default 0,
nopen integer not null default 0,
hash text,
size integer not null default 0,
pages integer not null default 0,
published date not null default -62135596800,
FOREIGN KEY (extid) REFERENCES extensions (id)
);
""",
"""
CREATE TABLE dirs (
id integer PRIMARY KEY NOT NULL,
name text
);
""",
"""
CREATE TABLE paths (
id integer PRIMARY KEY NOT NULL,
path text
)
""",
"""
CREATE TABLE filedir (
file integer NOT NULL,
dir integer NOT NULL,
PRIMARY KEY(dir, file),
FOREIGN KEY (dir) REFERENCES dirs (id) on delete cascade,
FOREIGN KEY (file) REFERENCES files (id) on delete cascade
);
""",
"""
CREATE TABLE parentdir (
parent integer NOT NULL,
id integer NOT NULL,
is_copy integer not null default 0,
hide integer not null default 0,
file_id integer not null default 0,
PRIMARY KEY(parent, id)
);
""",
"""
CREATE TABLE tags (
id integer PRIMARY KEY NOT NULL,
tag text NOT NULL
);
""",
"""
CREATE TABLE filetag (
fileid integer NOT NULL,
tagid integer NOT NULL,
PRIMARY KEY(fileid, tagid),
FOREIGN KEY (fileid) REFERENCES files (id) on delete cascade,
FOREIGN KEY (tagid) REFERENCES tags (id) on delete cascade
);
""",
"""
CREATE TABLE authors (
id integer PRIMARY KEY NOT NULL,
author text NOT NULL
);
""",
"""
CREATE TABLE fileauthor (
fileid integer NOT NULL,
aid integer NOT NULL,
PRIMARY KEY(fileid, aid),
FOREIGN KEY (aid) REFERENCES authors (id) on delete cascade,
FOREIGN KEY (fileid) REFERENCES files (id) on delete cascade
);
""",
"""
CREATE TABLE comments (
fileid integer NOT NULL,
id integer NOT NULL,
comment text NOT NULL,
created date not null default -62135596800,
modified date not null default -62135596800,
PRIMARY KEY(fileid, id),
FOREIGN KEY (fileid) REFERENCES files (id) on delete cascade
);
""",
"""
CREATE TABLE extensions (
id integer PRIMARY KEY NOT NULL,
extension text
);
""",
)
APP_ID = 1718185071
USER_VER = 6

def is_app_schema(db_name: str) -> bool:
    with apsw.Connection(db_name) as conn:
        try:
            v = conn.cursor().execute("PRAGMA application_id").fetchone()
        except apsw.NotADBError:
            return False
    return v[0] == APP_ID

def adjust_user_schema(db_name: str) -> int:
    with apsw.Connection(db_name) as conn:
        try:
            v = conn.cursor().execute("PRAGMA user_version").fetchone()
            if v[0] == USER_VER:
                return USER_VER
            if v[0] == 1:
                conn.cursor().execute(
                    'alter table parentdir add column hide integer '
                    'not null default 0; pragma user_version=2;'
                )
                v = (2,)
            if v[0] == 2:
                conn.cursor().execute(
                    'insert into settings (key) values (?)',
                    ('SHOW_HIDDEN',)
                )
                v = (3,)
            if v[0] == 3:
                conn.cursor().execute(
                    'PRAGMA user_version=4;'
                    'alter table parentdir add column file_id integer '
                    'not null default 0; pragma user_version=2;'
                )
                v = (4,)
            if v[0] == 4 or v[0] == 5:
                initialize_settings(conn)
                conn.cursor().execute(
                    'PRAGMA user_version=6;'
                )
                v = (6,)
            return v[0]
        except apsw.SQLError as err:
            # logger.info(err)
            return 0

def create_tables(db_name: str):
    conn = apsw.Connection(db_name)
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
        # logger.info(name)
        cursor.execute(sql, {'key': name})

def initiate_db(connection):
    """ insert "root" and "Lost" rows into table Dirs """
    connection.cursor().execute("insert into dirs values (0, null),(1, '@@Lost');")
    initialize_settings(connection)

if __name__ == "__main__":
    create_tables("ex000.db")
