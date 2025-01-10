# from loguru import logger
import apsw
from collections import deque, abc
from pathlib import PurePath

from PyQt6.QtWidgets import QMessageBox

from . import app_globals as ag, create_db


def dir_tree_select() -> list: # type: ignore
    sql2 = ('select p.parent, d.id, p.is_link, p.hide, p.file_id, '
               'COALESCE(p.tool_tip, d.name), d.name '
               'from dirs d join parentdir p on p.id = d.id '
               'where p.parent = :pid',
               'and p.hide = 0')
    sql = sql2[0] if ag.app.show_hidden.isChecked() else ' '.join(sql2)

    curs: apsw.Cursor = ag.db.conn.cursor()

    qu = deque()
    qu.append((0, []))

    while qu:
        dir_id, path = qu.pop()
        pp = [*path]
        pp.append(dir_id)
        rows = curs.execute(sql, {'pid': dir_id})
        for row in rows:
            qu.appendleft((row[1], pp))
            key = ','.join([str(p) for p in pp])
            yield key, row[-1], ag.DirData(*row[:-1])

def get_authors() -> apsw.Cursor:
    sql = 'select author, id from authors order by author COLLATE NOCASE;'
    return ag.db.conn.cursor().execute(sql)

def get_file_author_id(id: int) -> apsw.Cursor:
    sql = "select aid from fileauthor where fileid = ?"
    return ag.db.conn.cursor().execute(sql, (id,))

def get_file_authors(id: int) -> apsw.Cursor:
    sql = (
        'select author from authors a join fileauthor f on f.aid = a.id '
        'where f.fileid = ? order by author COLLATE NOCASE;'
    )
    return ag.db.conn.cursor().execute(sql, (id,))

def add_author(id: int, author: str) -> int:
    """
    id:  file id
    insert new author if doesn't exist
    and creates link between author and file
    if new author inserted returns its id
    else returns 0
    """
    sql1 = 'select id from authors where author = ?'
    sql2 = 'insert into authors (author) values (?);'
    sql3 = 'insert into fileauthor (aid, fileid) values (:a_id, :id)'

    author_id = 0
    with ag.db.conn as conn:
        cursor = conn.cursor()
        a_id = cursor.execute(sql1, (author,)).fetchone()
        if a_id:
            a_id = a_id[0]
        else:
            cursor.execute(sql2, (author,))
            a_id = conn.last_insert_rowid()
            author_id = a_id
        cursor.execute(sql3, {'a_id': a_id, 'id': id})
    return author_id

def break_file_authors_link(f_id: int, a_id: int):
    sql = 'delete from fileauthor where aid = :a_id and fileid = :f_id'
    ag.db.conn.cursor().execute(sql, {'a_id': a_id, 'f_id': f_id})

def update_author(id: int, val: str):
    sql = 'update authors set author = :name where id = :id'
    ag.db.conn.cursor().execute(sql, {'id': id, 'name': val})

def detele_author(id):
    sql = 'delete from authors where id = :id'
    with ag.db.conn as conn:
        conn.cursor().execute(sql, {'id': id})

def get_ext_list() -> apsw.Cursor:
    sql = (
        'select extension, id from extensions '
        'order by extension COLLATE NOCASE;'
    )
    return ag.db.conn.cursor().execute(sql)

#region files
def file_duplicates():
    sql = (
        'with x(hash, cnt) as ('
            'select hash, count(*) from files group by hash), '
        'y(hash, path, filename, id) as ('
            'select f.hash, p.path, f.filename, f.id '
            'from files f '
            'join paths p on p.id = f.path) '
        'select y.hash, y.path, y.filename, y.id from y '
        'join x on x.hash = y.hash '
        'where x.cnt > 1 order by y.hash'
    )
    return ag.db.conn.cursor().execute(sql)

def duplicate_count(file_id: int) -> int:
    sql = (
        'select count(*) from files where hash = '
        '(select hash from files where id = ?)'
    )
    return ag.db.conn.cursor().execute(sql, (file_id,)).fetchone()

def same_file_names_report():
    """
    file name, ext, path, size, file_id, count
    """
    sql = (
    'with x(fn, cnt) as ( '
        'select REPLACE(f.filename, "." || e.extension, "") as fn, count(*) as cnt '
        'from files f '
        'join extensions e on e.id = f.extid '
        'group by fn '
    ') , '
    'y(fn, ext, path, size, id) as ( '
        'select REPLACE(f.filename, "." || e.extension, "") as fn, '
        'e.extension as ext, p.path as path, f.size as size, f.id as id '
        'from files f '
        'join extensions e on e.id = f.extid '
        'join paths p on p.id = f.path '
    ') '
    'select y.fn, y.ext, y.path, y.size, y.id, x.cnt from y '
    'join x on x.fn = y.fn '
    'where x.cnt > 1'
    )
    return ag.db.conn.cursor().execute(sql)

def get_file_name(id: int|str) -> str:
    sql = 'select filename from files where id = ?'
    res = ag.db.conn.cursor().execute(sql, (id,)).fetchone()
    return res[0] if res else ''

def get_file_names() -> apsw.Cursor:
    return ag.db.conn.cursor().execute('select id, filename from files;')

def get_files(dir_id: int, parent: int) -> apsw.Cursor:
    sql = (
        'with x(fileid, last_note_date) as (select fileid, max(modified) '
        'from filenotes group by fileid) '
        'select f.filename, f.opened, f.rating, f.nopen, f.modified, f.pages, '
        'f.size, f.published, COALESCE(x.last_note_date, -62135596800), f.created, '
        'f.id, f.extid, f.path from files f '
        'left join x on x.fileid = f.id '
        'join filedir fd on fd.file = f.id '
        'join parentdir p on fd.dir = p.id '      # to avoid duplication
        'where fd.dir = :id and p.parent = :pid;'
    )
    return ag.db.conn.cursor().execute(sql, {'id': dir_id, 'pid': parent})

def get_found_files() -> apsw.Cursor:
    sql = (
        'with x(fileid, last_note_date) as (select fileid, max(modified) '
        'from filenotes group by fileid) '
        'select f.filename, f.opened, f.rating, f.nopen, f.modified, f.pages, '
        'f.size, f.published, COALESCE(x.last_note_date, -62135596800), f.created, '
        'f.id, f.extid, f.path from files f '
        'left join x on x.fileid = f.id '
        'where f.id in (select val from aux where key="file_srch");'
    )
    return ag.db.conn.cursor().execute(sql)

def get_file(file_id: int) -> abc.Iterable:
    sql = (
        'select f.filename, f.opened, f.rating, f.nopen, f.modified, f.pages, '
        'f.size, f.published, COALESCE(max(fn.modified), -62135596800), '
        'f.created, f.id, f.extid, f.path from files f '
        'left join filenotes fn on fn.fileid = f.id where f.id = :f_id;'
    )
    return ag.db.conn.cursor().execute(sql, {'f_id': file_id}).fetchone()

def lost_files():
    """
    put the lost files in a special folder and show it
    """
    # check if there are lost files
    sql0 = (
        'select 1 from files where id not in ('
        'select distinct file from filedir)'
    )
    # add lost files to @@Lost dir (dir_id=1)
    sql1 = (
        'insert into filedir select id,1 from files where id '
        'not in (select distinct file from filedir)'
    )
    # check if link to the @@Lost exists in dir tree
    sql2 = 'select 1 from parentdir where (parent,id) = (0,1)'
    # add hidden link into dir tree to folder @@Lost
    sql3 = 'insert into parentdir values (0, 1, 0, 1, 0, "@@Lost")'
    # clear @@Lost
    sql4 = 'delete from filedir where dir = 1'
    # check if the @@Lost dir exists
    sql5 = "select 1 from dirs where id = 1"
    # create @@Lost dir
    sql6 = "insert into dirs values (1, '@@Lost')"
    # clear @Lost from files that has copies in other dir(s)
    sql7 = (
        'with x(id, cnt) as (select file, count(*) '
        'from filedir where file in (select file '
        'from filedir where dir = 1) group by file) '
        'delete from filedir where dir = 1 and file '
        'in (select id from x where cnt > 1)'
    )


    def add_lost_in_tree():
        '''
        add @@Lost link (sql3) into dir tree (parentdir)
        if doesn't exist (sql2)
        '''
        lost_in_tree = conn.cursor().execute(sql2).fetchone()
        if not lost_in_tree:
            conn.cursor().execute(sql3)

    def create_lost_dir():
        '''
        create @@Lost dir (sql6) if doesn't exist (sql5)
        '''
        existLost = conn.cursor().execute(sql5).fetchone()
        if not existLost:
            conn.cursor().execute(sql6).fetchone()

    try:
        with ag.db.conn as conn:
            has_lost_files = conn.cursor().execute(sql0).fetchone()
            if not has_lost_files:
                # delete from @Lost dir files that has copies in other dir(s)
                conn.cursor().execute(sql7).fetchone()
                return

            create_lost_dir()

            conn.cursor().execute(sql4)   # clear @@Lost dir
            conn.cursor().execute(sql1)   # fill @@Lost dir

            add_lost_in_tree()
    finally:
        pass

def registered_file_id(path: str, filename: str) -> int:
    sql = (
        'select f.id from files f join paths p on p.id = f.path '
        'where f.filename = ? and p.path = ?'
    )
    res = ag.db.conn.cursor().execute(sql, (filename, path)).fetchone()
    return res[0] if res else 0

def get_path_id(path: str) -> int:
    sql1 = 'select id from paths where path = ?'
    sql2 = 'insert into paths (path) values (?)'
    with ag.db.conn as conn:
        curs = conn.cursor()
        res = curs.execute(sql1, (path,)).fetchone()
        if res:
            return res[0]
        curs.execute(sql2, (path,)).fetchone()
        return conn.last_insert_rowid()

def update_file_name_path(file_id: int, path_id: int, file_name: str):
    sql = 'update files set (filename, path) = (?, ?) where id = ?'
    ag.db.conn.cursor().execute(sql, (file_name, path_id, file_id))

def insert_file(file_: list) -> int:
    sql = (
        'insert into files (path, extid, hash, filename, '
        'modified, opened, created, rating, nopen, size, '
        'pages, published) values (?,?,?,?,?,?,?,?,?,?,?,?)'
    )

    def _get_path_id(conn: apsw.Connection) -> int:
        sql1 = 'select id from paths where path = ?'
        sql2 = 'insert into paths (path) values (?)'
        curs = conn.cursor()
        res = curs.execute(sql1, (file_[-1],)).fetchone()
        if res:
            return res[0]
        curs.execute(sql2, (file_[-1],)).fetchone()
        return conn.last_insert_rowid()

    def _get_ext_id(conn: apsw.Connection) -> int:
        sql1 = 'select id from extensions where extension = ?'
        sql2 = 'insert into extensions (extension) values (?)'
        ext = PurePath(file_[1]).suffix.strip('.')
        curs = conn.cursor()
        res = curs.execute(sql1, (ext,)).fetchone()
        if res:
            return res[0]
        curs.execute(sql2, (ext,)).fetchone()
        return conn.last_insert_rowid()

    with ag.db.conn as conn:
        path_id = _get_path_id(conn)
        ext_id = _get_ext_id(conn)
        conn.cursor().execute(sql, (path_id, ext_id, *file_[:-1]))
        return conn.last_insert_rowid()

def insert_tags(id, tags: list):
    """
    id - file id
    """
    sqls = [
        'select id from tags where tag = ?',
        'insert into tags (tag) values (?)',
        'insert into filetag values (?,?)',
    ]
    with ag.db.conn as conn:
        for tag in tags:
            tag_author_insert(conn, sqls, tag, id)

def insert_authors(id: int, authors: list):
    """
    id - file id
    """
    sqls = [
        'select id from authors where author = ?',
        'insert into authors (author) values (?)',
        'insert into fileauthor values (?,?)',
    ]
    with ag.db.conn as conn:
        for author in authors:
            tag_author_insert(conn, sqls, author, id)

def tag_author_insert(conn: apsw.Connection, sqls: list, item: str, id: int):
    cursor = conn.cursor()
    tt = cursor.execute(sqls[0], (item,)).fetchone()
    if tt:
        try:
            cursor.execute(sqls[2], (id, tt[0]))
        except apsw.ConstraintError:
            pass
    else:
        cursor.execute(sqls[1], (item,))
        t_id = conn.last_insert_rowid()
        cursor.execute(sqls[2], (id, t_id))

def insert_filenotes(id: int, file_notes: list):
    """
    id - file id
    """
    sql3 = (
        'insert into filenotes values (?,?,?,?,?)'
    )

    def get_max_note_id(cursor: apsw.Cursor) -> int:
        sql = 'select max(id) from filenotes where fileid = ?'

        tt = cursor.execute(sql, (id,)).fetchone()
        return tt[0] if tt[0] else 0

    def note_already_exists(cursor: apsw.Cursor, rec: list) -> bool:
        """
        suppose that there can't be more than one note
        for the same file created at the same time
        """
        sql = (
            'select 1 from filenotes where fileid = ? '
            'and created = ? and modified = ?'
        )
        tt = cursor.execute(sql, (id, rec[2], rec[3])).fetchone()
        return bool(tt)

    with ag.db.conn as conn:
        curs = conn.cursor()
        max_note_id = get_max_note_id(curs)

        for rec in file_notes:
            if note_already_exists(curs, rec):
                continue
            max_note_id += 1
            curs.execute(sql3, (id, max_note_id, *rec[1:]))

def recent_loaded_files() -> apsw.Cursor:
    sql = (
        'select f.id, f.filename, p.path from files f '
        'join paths p on p.id = f.path where f.size = 0'
    )
    return ag.db.conn.cursor().execute(sql)

def files_toched(last_scan: int) -> apsw.Cursor:
    sql = (
        'select f.id, f.filename, p.path, f.hash from files f '
        'join paths p on p.id = f.path where f.opened > ?'
    )
    return ag.db.conn.cursor().execute(sql, (last_scan,))

def get_pdf_files() -> apsw.Cursor:
    sql = (
        "select f.id, f.filename, p.path from files f "
        "join paths p on p.id = f.path "
        "join extensions e on e.id = f.extid "
        "where f.pages = 0 and e.extension = 'pdf'"
    )
    return ag.db.conn.cursor().execute(sql)

def update_file_data(id, st, hash):
    hs = (', hash', ',?') if hash else ('','')
    sql = (
        f'update files set (modified, created, size{hs[0]}) '
        f'= (?, ?, ?{hs[1]}) where id = ?'
    )
    ag.db.conn.cursor().execute(
        sql, (int(st.st_mtime), int(st.st_ctime),
        st.st_size, hash, id) if hash else
        (int(st.st_mtime), int(st.st_ctime), st.st_size, id)
    )

def update_pdf_file(id, pages, p_date):
    sql = (
        'update files set (pages, published) = (?, ?) where id = ?'
    )
    ag.db.conn.cursor().execute(sql, (pages, p_date))

def filter_files(param: dict) -> apsw.Cursor:
    par = []
    cond = []
    sqlist = []

    def filter_sqls(key: str, field: str='') -> str:
        return {
            'dir_sql': "select distinct val from aux where key = 'files_dir'",
            'tag_sql': "select val from aux where key = 'file_tag'",
            'ext_sql': (
                "select id from files where extid in "
                "(select val from aux where key = 'ext')"
            ),
            'author_sql': (
                "select fileid from fileauthor where aid in "
                "(select val from aux where key = 'author')"
            ),
            'sql0': (
                'with x(fileid, last_note_date) as (select fileid, max(modified) '
                'from filenotes group by fileid) '
                'select f.filename, f.opened, f.rating, f.nopen, f.modified, f.pages, '
                'f.size, f.published, COALESCE(x.last_note_date, -62135596800), f.created, '
                'f.id, f.extid, f.path from files f '
                'left join x on x.fileid = f.id '
            ),
            'open-0': "nopen <= ?",
            'open-1': "nopen > ?",
            'rating-0': "rating < ?",
            'rating-1': "rating = ?",
            'rating-2': "rating > ?",
            'after': f"{field} > ?",
            'before': f"{field} < ?",
        }[key]

    def filter_subsqls():
        if param['dir']:
            sqlist.append(filter_sqls('dir_sql'))
        if param['tag']:
            sqlist.append(filter_sqls('tag_sql'))
        if param['ext']:
            sqlist.append(filter_sqls('ext_sql'))
        if param['author']:
            sqlist.append(filter_sqls('author_sql'))

    def filter_parcond():
        if param['open_check']:
            cond.append(filter_sqls(f'open-{param["open_op"]}'))
            par.append(param['open_val'])
        if param['rating_check']:
            cond.append(filter_sqls(f'rating-{param["rating_op"]}'))
            par.append(param['rating_val'])
        if param['after']:
            cond.append(filter_sqls('after', param["date"]))
            par.append(param['date_after'])
        if param['before']:
            cond.append(filter_sqls('before', param["date"]))
            par.append(param['date_before'])

    def assemble_filter_sql() -> str:
        if sqlist:
            sqlist[-1] = f"{sqlist[-1]})"            # add right parenthesis
            sql1 = ''.join((
                filter_sqls('sql0'),
                'where f.id in (',
                ' intersect '.join(sqlist)))
            sql = ' and '.join((sql1, *cond)) if cond else sql1
        else:
            sql1 = filter_sqls('sql0')
            sql = ' '.join((sql1, 'where', ' and '.join(cond))) if cond else sql1
        return sql

    filter_subsqls()

    filter_parcond()

    sql = assemble_filter_sql()

    return (
        ag.db.conn.cursor().execute(sql, tuple(par))
        if par else ag.db.conn.cursor().execute(sql)
    )

def delete_not_exist_file(id: int):
    sql_del = 'delete from files where id = ?'
    ag.db.conn.cursor().execute(sql_del, (id,))

def delete_file(id: int):
    """
    delete file, esential info about file
    will be tied to one of its duplicates if any
    """
    sql_hash = 'select hash from files where id = :be_removed'
    sql_sta = (
        'select count(*), sum(nopen), max(rating), max(modified), '
        'max(opened) from files where hash = ?'
    )
    sql_preserve_id = (
        'select id from files where hash = :hash and id != :be_removed'
    )
    sql_max_id = 'select max(id) from filenotes where fileid = :preserved'
    sql_upd_filenotes = (
        'update filenotes set fileid = :preserved, '
        'id = id+:max_id where fileid = :be_removed '
    )
    sql_upd_file = (
        'update files set nopen = :num, rating = :rate, '
        'modified = :modi, opened = :opnd where id = :preserved'
    )
    sql_upd_tags = (
        'update filetag set fileid = :preserved '
        'where fileid = :be_removed'
    )
    sql_upd_authors = (
        'update fileauthor set fileid = :preserved '
        'where fileid = :be_removed'
    )
    sql_del = 'delete from files where id = ?'

    def update_preserve():
        """
        file notes, rating and number of openings will be
        tied to one of the saved files among its duplicates
        """
        hash = curs.execute(sql_hash, {'be_removed': id}).fetchone()
        if not hash:
            return
        sta = curs.execute(sql_sta, (hash[0],)).fetchone()
        if sta[0] > 1:  # if duplicates exists
            preserve_id = curs.execute(
                sql_preserve_id,
                {'hash': hash[0], 'be_removed': id}
            ).fetchone()[0]
            _id = curs.execute(
                sql_max_id, {'preserved': preserve_id}
            ).fetchone()[0]
            max_id = _id if _id else 0
            curs.execute(
                sql_upd_filenotes,
                {
                    'preserved': preserve_id,
                    'max_id': max_id,
                    'be_removed': id
                }
            )
            curs.execute(
                sql_upd_file,
                {
                    'num': sta[1],
                    'rate': sta[2],
                    'modi': sta[3],
                    'opnd': sta[4],
                    'preserved': preserve_id
                }
            )
            curs.execute(
                sql_upd_tags,
                {
                    'preserved': preserve_id,
                    'be_removed': id
                }
            )
            curs.execute(
                sql_upd_authors,
                {
                    'preserved': preserve_id,
                    'be_removed': id
                }
            )

    with ag.db.conn as conn:
        curs = conn.cursor()
        update_preserve()
        curs.execute(sql_del, (id,))

def delete_file_dir_link(id: int, dir_id: int):
    sql = 'delete from filedir where file = ? and dir = ?'
    ag.db.conn.cursor().execute(sql, (id, dir_id))

def get_file_dir_ids(file_id: int) -> apsw.Cursor:
    sql_id = 'select file, dir from filedir where file = ?'
    sql_hash = (
        'select file, dir from filedir where file in '
        '(select id from files where hash = ?)'
    )
    hash_ = get_file_hash(file_id)
    if hash_:
        return ag.db.conn.cursor().execute(sql_hash, (hash_,))
    else:
        return ag.db.conn.cursor().execute(sql_id, (file_id,))

def get_dir_id_for_file(file_id: int) -> int:
    sql = 'select dir from filedir where file = ?'
    res = ag.db.conn.cursor().execute(sql, (file_id,)).fetchone()
    return res[0] if res else 0

def temp_files_dir(dirs: list, sub_dirs: bool):
    sql0 = "insert into aux values ('dir', ?)"
    sql1 = (
        "with x(id) as (select id from parentdir where parent = ? "
        "union select t.id from x inner join parentdir t "
        "on t.parent = x.id) select * from x"
    )
    sql2 = (
        "insert into aux(key, val) select 'files_dir', file from "
        "filedir where dir in (select val from aux where key = 'dir')"
    )
    curs = ag.db.conn.cursor()
    if sub_dirs:
        dir_ = set(dirs)
        for dd in dirs:
            scur = curs.execute(sql1, dd)
            for s in scur:
                dir_.add(s)
        curs.executemany(sql0, dir_)
    else:
        curs.executemany(sql0, dirs)

    curs.execute(sql2)

def clear_temp():
    sql = "delete from aux where key != 'TREE_PATH'"
    ag.db.conn.cursor().execute(sql)

def save_to_temp(key: str, val):
    ag.db.conn.cursor().execute(
        "insert into aux values (?, ?)", (key, val))

def save_branch_in_aux(path):
    sql = 'update aux set val = :path where key = :key'
    key = 'TREE_PATH'
    ag.db.conn.cursor().execute(sql, {'path': path, 'key': key})

def get_branch_from_aux() -> str:
    sql = 'select val from aux where key = ?'
    key = 'TREE_PATH'
    res = ag.db.conn.cursor().execute(sql, (key,)).fetchone()
    return res[0] if res else ''

def get_file_path(id: int) -> str:
    sql = (
        'select p.path, f.filename from files f '
        'join paths p on p.id = f.path '
        'where f.id = ?'
    )
    res = ag.db.conn.cursor().execute(sql, (id,)).fetchone()
    return '/'.join(res) if res else ''

def get_file_info(id: int) -> apsw.Cursor:
    sql = (
        'select f.filename, p.path, f.opened, f.modified, f.created, '
        'f.published, f.nopen, f.rating, f.size, f.pages from files f '
        'join paths p on p.id = f.path where f.id = ?'
    )
    return ag.db.conn.cursor().execute(sql, (id,)).fetchone()

def move_file(new_dir: int, old_dir: int, file_id: int):
    sql ='update filedir set dir = :new where dir = :old and file = :id;'
    with ag.db.conn as conn:
        try:
            conn.cursor().execute(
                sql, {'new': new_dir, 'old': old_dir, 'id': file_id}
            )
        except apsw.ConstraintError:
            pass         # re-copy, duplication

def copy_file(file_id: int, dir_id: int):
    sql = 'insert into filedir (file, dir) values (?, ?);'
    with ag.db.conn as conn:
        try:
            conn.cursor().execute(sql, (file_id, dir_id))
        except apsw.ConstraintError:
            pass         # re-copy, duplication

def update_opened_file(id: int) -> int:
    """
    return new unixepoch timestamp, or -1 if not created
    """
    sql0 = "select opened from files where id = ?"
    sql1 = "update files set (opened, nopen) = (unixepoch(), nopen+1) where id = ?"
    with ag.db.conn as conn:
        curs = conn.cursor()
        ts0 = curs.execute(sql0, (id,)).fetchone()
        curs.execute(sql1, (id,))
        ts = curs.execute(sql0, (id,)).fetchone()
        return ts[0] if ts[0] > ts0[0] else -1

def update_files_field(id: int, field: str, val):
    #  rating, Pages, published
    sql = f'update files set {field} = ? where id = ?'
    with ag.db.conn as conn:
        conn.cursor().execute(sql, (val, id))

def get_export_data(fileid: int) -> dict:
    sql1 = (
        'select f.hash, f.filename, f.modified, f.opened, '
        'f.created, f.rating, f.nopen, f.size, f.pages, '
        'f.published, p.path from files f join paths p '
        'on p.id = f.path where f.id = ?'
    )
    sql2 = (
        'select id, filenote, created, modified '
        'from filenotes where fileid = ?'
    )
    sql3 = (
        'select t.tag from tags t join filetag f on '
        'f.tagid = t.id where f.fileid = ?'
    )
    sql4 = (
        'select a.author from authors a join fileauthor f on '
        'f.aid = a.id where f.fileid = ?'
    )

    res = {}
    with ag.db.conn as conn:
        cursor = conn.cursor()
        tt = cursor.execute(sql1, (fileid,)).fetchone()
        if not tt:
            return None
        res['file'] = tt

        tt = []
        for cc in cursor.execute(sql2, (fileid,)):
            tt.append(cc)
        res['notes'] = tt

        tt = []
        for cc in cursor.execute(sql3, (fileid,)):
            tt.append(cc[0])
        res['tags'] = tt

        tt = []
        for cc in cursor.execute(sql4, (fileid,)):
            tt.append(cc[0])
        res['authors'] = tt

    return res
#endregion

def update_tooltip(data: ag.DirData):
    sql1 = 'select name from dirs where id = ?'
    sql2 = 'update parentdir set tool_tip = ? where parent = ? and id = ?'
    with ag.db.conn as conn:
        curs = conn.cursor()
        dir_name = curs.execute(sql1, (data.id,)).fetchone()
        tip = None if dir_name[0] == data.tool_tip else data.tool_tip
        curs.execute(
            sql2, (tip, data.parent_id, data.id)
        )

def update_dir_name(name: str, data: ag.DirData):
    sql1 = 'update dirs set name = ? where id = ?'
    sql2 = 'update parentdir set tool_tip = null where parent = ? and id = ?'
    with ag.db.conn as conn:
        conn.cursor().execute(sql1, (name, data.id))
        if name == data.tool_tip:
            conn.cursor().execute(sql2, (data.parent_id, data.id))

def update_file_id(d_data: ag.DirData):
    sql = 'update parentdir set file_id = ? where parent = ? and id = ?'

    with ag.db.conn as conn:
        conn.cursor().execute(
            sql, (d_data.file_id, d_data.parent_id, d_data.id)
        )

def insert_dir(dir_name: str, parent: int) -> int:
    sql2 = 'insert into dirs (name) values (?);'
    sql3 = 'insert into parentdir values (?, ?, 0, 0, 0, ?);'
    with ag.db.conn as conn:
        curs = conn.cursor()
        curs.execute(sql2, (dir_name,))
        id = conn.last_insert_rowid()
        curs.execute(sql3, (parent, id, dir_name))
    return id

def copy_existent(file_id: int, parent_dir: int) -> int:
    """
    make copy of existent file while import from file
    """
    sql = (  # the "existent" folder id in the current folder if any
        'select d.id from dirs d join parentdir p on '
        'p.id = d.id where p.parent = ? and d.name = ?'
    )
    id = ag.db.conn.cursor().execute(sql, (parent_dir, 'existent')).fetchone()
    exist_id = id[0] if id else insert_dir('existent', parent_dir)
    copy_file(file_id, exist_id)
    return exist_id

def toggle_hidden_dir_state(id: int, parent: int, hidden: bool):
    sql = 'update parentdir set hide = :hide where (id,parent) = (:id,:parent)'
    with ag.db.conn as conn:
        conn.cursor().execute(sql, {'hide':hidden, 'id':id, 'parent':parent})

def dir_parents(dir_id: int) -> apsw.Cursor:
    sql = 'select parent from parentdir where id = ?'
    return ag.db.conn.cursor().execute(sql, (dir_id,))

def dir_min_parent(dir_id: int) -> int:
    sql = 'select parent from parentdir where id = ?'
    parent = ag.db.conn.cursor().execute(sql, (dir_id,)).fetchone()
    return parent[0]

def dir_children(id: int) -> apsw.Cursor:
    sql = 'select * from parentdir where parent = ?'
    with ag.db.conn as conn:
        curs = conn.cursor()
        return curs.execute(sql, (id,))

def get_dir_name(id: int) -> str:
    sql = 'select name from dirs where id = ?'
    res = ag.db.conn.cursor().execute(sql, (id,)).fetchone()
    return res[0] if res else ''

def delete_dir(id: int, parent: int):
    """
    delete dir with all children if any
    """
    sql1 = 'delete from parentdir where id = ?'
    sql2 = 'delete from dirs where id = ?'

    with ag.db.conn as conn:
        curs: apsw.Cursor = conn.cursor()
        curs.execute(sql1, (id,))
        curs.execute(sql2, (id,))

def remove_dir_copy(id: int, parent: int):
    sql = 'delete from parentdir where (parent, id) = (?,?)'
    with ag.db.conn as conn:
        conn.cursor().execute(sql, (parent, id))

def copy_dir(parent: int, dir_data: ag.DirData) -> bool:
    sql = 'insert into parentdir values (?, ?, 1, 0, ?, ?);'
    with ag.db.conn as conn:
        try:
            conn.cursor().execute(
                sql, (parent, dir_data.id, dir_data.file_id, dir_data.tool_tip)
            )
            return True
        except apsw.ConstraintError:
            return False   # silently, dir copy already exists

def move_dir(new: int, old: int, id: int) -> bool:
    """
    new - new parent id;
    old - old parent id;
    id  - id of moved dir;
    """
    sql = 'update parentdir set parent = :new where parent = :old and id = :id;'
    with ag.db.conn as conn:
        try:
            conn.cursor().execute(sql, {"id": id, "old": old, "new": new})
            return True
        except apsw.ConstraintError:
            return False   # dir can't be moved here, already exists

def get_file_hash(file_id: int) -> str:
    hash_sql = "select hash from files where id = ?"
    hash_ = ag.db.conn.cursor().execute(hash_sql, (file_id,)).fetchone()
    return hash_[0] if hash_ else ''

def get_file_id_to_notes(file_id: int) -> int:
    """
    returns the minimum file_id in duplicate files
    """
    sql = 'select min(id) from files where hash = ?'
    hash_ = get_file_hash(file_id)

    if hash_:
        f_id = ag.db.conn.cursor().execute(sql, (hash_,)).fetchone()
        return f_id[0]
    return file_id

def get_file_notes(file_id: int, desc: bool=False) -> apsw.Cursor:
    sql_hash = (
        "select filenote, fileid, id, modified, created from filenotes "
        "where fileid in (select id from files where hash = ?) "
        "order by modified"
    )
    sql_id = (
        "select filenote, fileid, id, modified, created from filenotes "
        "where fileid  = ? order by modified"
    )
    if file_id <= 0:
        return []
    hash_ = get_file_hash(file_id)

    if hash_:
        sql = ' '.join((sql_hash, 'desc')) if desc else sql_hash
        par = hash_
    else:       # hash not calculated yet
        sql = ' '.join((sql_id, 'desc')) if desc else sql_id
        par = file_id

    with ag.db.conn as conn:
        return conn.cursor().execute(sql, (par,))

def get_note(file: int, note: int) -> str:
    sql = 'select filenote from filenotes where fileid = ? and id = ?;'
    note_text = ag.db.conn.cursor().execute(sql, (file, note)).fetchone()
    return '' if (note_text is None) else note_text[0]

def get_all_notes() -> apsw.Cursor:
    sql = 'select fileid, filenote from filenotes;'
    return ag.db.conn.cursor().execute(sql)

def insert_note(fileid: int, note: str) -> int:
    sql1 = 'select max(id) from filenotes where fileid=?;'
    sql2 = ('insert into filenotes (fileid, id, filenote, modified, '
        'created) values (:fileid, :id, :filenote, :modified, :created);')
    with ag.db.conn as conn:
        curs = conn.cursor()
        last_note_id = curs.execute(sql1, (fileid,)).fetchone()
        new_note_id = last_note_id[0]+1 if last_note_id[0] else 1
        ts = curs.execute('select unixepoch()').fetchone()

        curs.execute(sql2,
            {
                'fileid': fileid,
                'id': new_note_id,
                'filenote': note,
                'modified': ts[0],
                'created': ts[0]
            }
        )
        return ts[0]

def update_note(fileid: int, id: int, note: str) -> int:
    sql0 = 'select modified from filenotes where fileid=:fileid and id=:id'
    sql1 = ('update filenotes set (filenote, modified) = (:filenote, unixepoch()) '
        'where fileid=:fileid and id=:id')
    with ag.db.conn as conn:
        curs = conn.cursor()
        ts0 = curs.execute(sql0,{ 'fileid': fileid, 'id': id, }).fetchone()
        curs.execute(sql1,
            {
                'fileid': fileid,
                'id': id,
                'filenote': note,
            }
        )
        ts = curs.execute(sql0,{ 'fileid': fileid, 'id': id, }).fetchone()
        return ts[0] if ts[0] > ts0[0] else -1

def delete_note(file: int, note: int):
    sql = 'delete from filenotes where fileid = ? and id = ?;'
    ag.db.conn.cursor().execute(sql, (file, note))

def delete_file_notes(file: int):
    sql = 'delete from filenotes where fileid = ?;'
    ag.db.conn.cursor().execute(sql, (file,))

def get_tags() -> apsw.Cursor:
    sql = 'select Tag, ID from Tags order by Tag COLLATE NOCASE;'
    return ag.db.conn.cursor().execute(sql)

def get_file_tags(file_id: int) -> apsw.Cursor:
    sql = ('select Tag, ID from Tags where ID in '
        '(select TagID from FileTag where FileID = ?);')
    return ag.db.conn.cursor().execute(sql, (file_id,))

def get_file_tagid(file_id: int) -> apsw.Cursor:
    sql = 'select TagID from FileTag where FileID = ?'
    return ag.db.conn.cursor().execute(sql, (file_id,))

def insert_tag(tag: str) -> int:
    sql = "insert into Tags (Tag) values (:tag);"
    ag.db.conn.cursor().execute(sql, {'tag': tag})
    return ag.db.conn.last_insert_rowid()

def insert_tag_file(tag: int, file: int):
    sql = 'insert into filetag (tagid, fileid) values (:tag_id, :file_id);'
    try:
        ag.db.conn.cursor().execute(sql, {'tag_id': tag, 'file_id': file})
    except apsw.ConstraintError:
        pass

def delete_tag_file(tag: int, file: int):
    sql = 'delete from filetag where (tagid, fileid) = (:tag, :file)'
    try:
        ag.db.conn.cursor().execute(sql, {'tag': tag, 'file': file})
    except apsw.ConstraintError:
        pass

def update_file_tag_links(file: int, tags: list[int]):
    """
    only the deletion of file-tag links is done here
    the links addition is already done when the tags list was being prepared
    """
    sql1 = 'select tagid from filetag where fileid = ?'
    sql2 = 'delete from filetag where (tagid, fileid) = (:tag, :file)'
    with ag.db.conn as conn:
        curs1: apsw.Cursor = conn.cursor()
        curs2: apsw.Cursor = conn.cursor()
        old_tags = curs1.execute(sql1, (file,))
        for tag in old_tags:
            if tag[0] in tags:
                continue
            curs2.execute(sql2, {'tag': tag[0], 'file': file})

def update_tag(id: int, val: str):
    sql = 'update tags set tag = :tag where id = :id'
    with ag.db.conn as conn:
        conn.cursor().execute(sql, {'id': id, 'tag': val})

def detele_tag(id):
    sql = 'delete from tags where id = :id'
    with ag.db.conn as conn:
        conn.cursor().execute(sql, {'id': id})

def get_files_tag(tag: int) -> set[int]:
    sql = 'select fileid from FileTag where tagid = ?'
    curs = ag.db.conn.cursor().execute(sql, (tag,))
    files = []
    for id in curs:
        files.append(id[0])
    return set(files)

def create_connection(path: str) -> bool:
    if not path:
        return False
    try:
        conn: apsw.Connection = apsw.Connection(path)
    except apsw.CantOpenError as e:
        ag.show_message_box(
            'Error open DB',
            f'{e.args}, DB file: {path}',
            icon=QMessageBox.Icon.Critical
        )
        return False

    ag.db.path = path
    ag.db.conn = conn

    if not create_db.tune_new_version():
        ag.db.path = ''
        ag.db.conn = None
        return False

    ag.signals_.user_signal.emit('Enable_buttons')

    cursor = conn.cursor()
    cursor.execute('pragma foreign_keys = ON;')
    cursor.execute('pragma temp_store = MEMORY;')
    cursor.execute('pragma busy_timeout=1000')

    cursor.execute('create temp table if not exists aux (key, val)')
    save_to_temp("TREE_PATH", '')

    return True