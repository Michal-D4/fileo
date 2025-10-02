# from loguru import logger
import apsw
from collections import deque, abc
from pathlib import Path

from PyQt6.QtWidgets import QStyle

from . import app_globals as ag, create_db


def dir_tree_select() -> list: # type: ignore
    sql2 = ('select p.parent, d.id, d.multy, p.hide, p.file_id, '
               'COALESCE(p.tool_tip, d.name), d.name '
               'from dirs d join parentdir p on p.id = d.id '
               'where p.parent = :pid',
               'and p.hide = 0',
               'order by d.name collate nocase')
    sql = ' '.join(sql2[::2] if ag.app.show_hidden.isChecked() else sql2)

    curs: apsw.Cursor = ag.db.conn.cursor()

    qu = deque()
    qu.append((0, []))

    while qu:
        dir_id, path = qu.pop()
        pp = [*path]
        pp.append(dir_id)
        for row in curs.execute(sql, {'pid': dir_id}):
            qu.appendleft((row[1], pp))
            key = ','.join([str(p) for p in pp])
            yield key, row[-1], ag.DirData(*row[:-1])

def get_authors() -> apsw.Cursor:
    sql = 'select author, id from authors order by author COLLATE NOCASE;'
    return ag.db.conn.cursor().execute(sql)

def get_file_author_id(id: int) -> apsw.Cursor:
    sql = "select aid from fileauthor where fileid = ?"
    return ag.db.conn.cursor().execute(sql, (id,))

def insert_author(author: str) -> int:
    sql = 'insert into authors (author) values (?);'
    ag.db.conn.cursor().execute(sql, (author,))
    return ag.db.conn.last_insert_rowid()

def insert_file_author(a_id: int, f_id: int):
    sql = 'insert into fileauthor (aid, fileid) values (:author_id, :file_id)'
    try:
        ag.db.conn.cursor().execute(sql, {'author_id': a_id, 'file_id': f_id})
    except apsw.ConstraintError:
        pass         # ignore, duplication

def break_file_authors_link(f_id: int, a_id: int):
    sql = 'delete from fileauthor where (aid, fileid) = (:a_id, :f_id)'
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
            'join paths p on p.id = f.path where f.size > 0) '
        'select y.hash, y.path, y.filename, y.id from y '
        'join x on x.hash = y.hash '
        'where x.cnt > 1 order by y.hash'
    )
    return ag.db.conn.cursor().execute(sql)

def duplicate_count(file_id: int) -> int:
    sql = (
        'select count(*) from files where hash = '
        '(select hash from files where id = ? and size > 0 and hash != "")'
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
        'select f.filename, f.added, f.opened, f.rating, f.nopen, f.modified, f.pages, '
        'f.size, f.published, COALESCE(x.last_note_date, -62135596800), f.created, '
        'f.id from files f '
        'left join x on x.fileid = f.id '
        'join filedir fd on fd.file = f.id '
        'join parentdir p on fd.dir = p.id '      # to avoid duplication
        'where (fd.dir, p.parent) = (:id, :pid);'
    )
    return ag.db.conn.cursor().execute(sql, {'id': dir_id, 'pid': parent})

def get_found_files() -> apsw.Cursor:
    sql = (
        'with x(fileid, last_note_date) as (select fileid, max(modified) '
        'from filenotes group by fileid) '
        'select f.filename, f.added, f.opened, f.rating, f.nopen, f.modified, f.pages, '
        'f.size, f.published, COALESCE(x.last_note_date, -62135596800), f.created, '
        'f.id from files f '
        'left join x on x.fileid = f.id '
        'where f.id in (select val from aux where key="file_srch");'
    )
    return ag.db.conn.cursor().execute(sql)

def get_file(file_id: int) -> abc.Iterable:
    sql = (
        'select f.filename, f.added, f.opened, f.rating, f.nopen, f.modified, f.pages, '
        'f.size, f.published, COALESCE(max(fn.modified), -62135596800), '
        'f.created, f.id from files f '
        'left join filenotes fn on fn.fileid = f.id where f.id = :f_id;'
    )
    return ag.db.conn.cursor().execute(sql, {'f_id': file_id}).fetchone()

def registered_file_id(path: str, filename: str) -> int:
    sql = (
        'select f.id from files f join paths p on p.id = f.path '
        'where (f.filename, p.path) = (?,?)'
    )
    res = ag.db.conn.cursor().execute(sql, (filename, path)).fetchone()
    return res[0] if res else 0

def get_path_id(path: str) -> int:
    sql1 = 'select id from paths where path = ?'
    sql2 = 'insert into paths (path) values (?)'
    path = Path(path).as_posix()
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

def file_add_reason(file_id: int) -> ag.fileSource:
    sql = 'select how_added from files where id = ?'
    rsn = ag.db.conn.cursor().execute(sql, (file_id,)).fetchone()
    return ag.fileSource(rsn[0]) if rsn else ag.fileSource.SCAN_SYS

def insert_file(file_data: list, added: int, how_added: int) -> tuple[int, bool]:
    sql = (
        'insert into files (path, extid, hash, filename, '
        'modified, opened, created, rating, nopen, size, '
        'pages, published, added, how_added) '
        'values (?,?,?,?,?,?,?,?,?,?,?,?,?,?)'
    )

    def _get_ext_id() -> tuple[int, bool]:
        """
        extension is considered case-insensitive in the app.
        This only influence to the filter - file extensions
        are considered as the same iregardless of case.
        However, when opening a file, it opens with
        its actual extension.
        """
        sql1 = 'select id from extensions where lower(extension) = ?'
        sql2 = 'insert into extensions (extension) values (?)'
        ext = Path(file_data[1]).suffix.strip('.')
        curs = conn.cursor()
        res = curs.execute(sql1, (ext.lower(),)).fetchone()
        if res:
            return res[0], False
        curs.execute(sql2, (ext,)).fetchone()
        return conn.last_insert_rowid(), True

    with ag.db.conn as conn:
        path_id = get_path_id(file_data[-1])
        ext_id, is_new = _get_ext_id()
        conn.cursor().execute(sql, (path_id, ext_id, *file_data[:-1], added, how_added))
        return conn.last_insert_rowid(), is_new

def insert_tags(file_id, tags: list) -> bool:
    sqls = [
        'select id from tags where tag = ?',
        'insert into tags (tag) values (?)',
        'insert into filetag values (?,?)',
    ]
    new_tags = False
    with ag.db.conn as conn:
        for tag in tags:
            new_tags |= tag_author_insert(conn, sqls, tag, file_id)
    return new_tags

def insert_authors(file_id: int, authors: list) -> bool:
    sqls = [
        'select id from authors where author = ?',
        'insert into authors (author) values (?)',
        'insert into fileauthor values (?,?)',
    ]
    new_authors = False
    with ag.db.conn as conn:
        for author in authors:
            new_authors |= tag_author_insert(conn, sqls, author, file_id)
    return new_authors

def tag_author_insert(conn: apsw.Connection, sqls: list, name: str, file_id: int) -> bool:
    cursor = conn.cursor()
    tt = cursor.execute(sqls[0], (name,)).fetchone()
    if tt:
        try:
            cursor.execute(sqls[2], (file_id, tt[0]))
        except apsw.ConstraintError:
            pass         # ignore, author duplication
        return False
    cursor.execute(sqls[1], (name,))
    t_id = conn.last_insert_rowid()
    cursor.execute(sqls[2], (file_id, t_id))
    return True          # new tag / author inserted

def insert_filenotes(file_id: int, file_notes: list):
    if len(file_notes) == 0:
        return
    sql3 = 'insert into filenotes values (?,?,?,?,?)'

    def get_max_note_id() -> int:
        sql = 'select max(id) from filenotes where fileid = ?'

        tt = cursor.execute(sql, (file_id,)).fetchone()
        return tt[0] if tt[0] else 0

    def note_already_exists() -> bool:
        """
        suppose that there can't be more than one note for the same file
        with the same creation and modification time
        """
        sql = 'select 1 from filenotes where (fileid, created, modified) = (?,?,?) '
        tt = cursor.execute(sql, (file_id, rec[4], rec[3])).fetchone()
        return bool(tt)

    with ag.db.conn as conn:
        cursor = conn.cursor()
        max_note_id = get_max_note_id()

        for rec in file_notes:
            if note_already_exists():
                continue
            max_note_id += 1
            cursor.execute(sql3, (file_id, max_note_id, rec[0], rec[4], rec[3]))

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

def filter_files(checks: dict) -> apsw.Cursor:
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
            'note_date': "select val from aux where key = 'note_date_files'",
            'sql0': (
                'with x(fileid, last_note_date) as (select fileid, max(modified) '
                'from filenotes group by fileid) '
                'select f.filename, f.added, f.opened, f.rating, f.nopen, f.modified, '
                'f.pages, f.size, f.published, COALESCE(x.last_note_date, -62135596800), '
                'f.created, f.id from files f '
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
        if checks['dir'] or checks['no_dir'] or checks['add_method']:
            sqlist.append(filter_sqls('dir_sql'))
        if checks['tag']:
            sqlist.append(filter_sqls('tag_sql'))
        if checks['ext']:
            sqlist.append(filter_sqls('ext_sql'))
        if checks['author']:
            sqlist.append(filter_sqls('author_sql'))
        if checks['note date is set']:
            sqlist.append(filter_sqls('note_date'))

    def filter_parcond():
        if checks['open_check']:
            cond.append(filter_sqls(f'open-{checks["open_op"]}'))
            par.append(checks['open_val'])
        if checks['rating_check']:
            cond.append(filter_sqls(f'rating-{checks["rating_op"]}'))
            par.append(checks['rating_val'])
        if checks["date"] != "note_date":
            if checks['after']:
                cond.append(filter_sqls('after', checks["date"]))
                par.append(checks['date_after'])
            if checks['before']:
                cond.append(filter_sqls('before', checks["date"]))
                par.append(checks['date_before'])

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

def delete_file(file_id: int):
    """
    delete file, esential info about file
    will be tied to one of its duplicates if any
    """
    sql_sta = (
        'select count(*), sum(nopen), max(rating), max(modified), '
        'max(opened) from files where hash = ?'
    )
    sql_saved_id = (
        'select id from files where hash = :hash and id != :be_removed'
    )
    sql_max_id = 'select max(id) from filenotes where fileid = :saved_id'
    sql_upd_filenotes = (
        'update filenotes set fileid = :saved_id, '
        'id = id+:max_id where fileid = :be_removed '
    )
    sql_upd_file = (
        'update files set nopen = :num, rating = :rate, '
        'modified = :modi, opened = :opnd where id = :saved_id'
    )
    sql_upd_tags = (
        'update filetag set fileid = :saved_id '
        'where fileid = :be_removed'
    )
    sql_upd_authors = (
        'update fileauthor set fileid = :saved_id '
        'where fileid = :be_removed'
    )
    sql_del = 'delete from files where id = ?'

    def update_with_saved():
        """
        file notes, rating and number of openings will be
        tied to one of the saved files among its duplicates
        """
        hash = get_file_hash(file_id)
        if not hash:
            return
        sta = curs.execute(sql_sta, (hash,)).fetchone()
        if sta[0] > 1:  # if duplicates exists
            saved_id = curs.execute(
                sql_saved_id,
                {'hash': hash, 'be_removed': file_id}
            ).fetchone()[0]
            _id = curs.execute(
                sql_max_id, {'saved_id': saved_id}
            ).fetchone()[0]
            max_note_id = _id if _id else 0
            curs.execute(
                sql_upd_filenotes,
                {
                    'saved_id': saved_id,
                    'max_id': max_note_id,
                    'be_removed': file_id
                }
            )
            curs.execute(
                sql_upd_file,
                {
                    'num': sta[1],
                    'rate': sta[2],
                    'modi': sta[3],
                    'opnd': sta[4],
                    'saved_id': saved_id
                }
            )
            try:
                curs.execute(sql_upd_tags,
                    {'saved_id': saved_id, 'be_removed': file_id}
                )
            except apsw.ConstraintError:
                pass         # ignore, tag duplication
            try:
                curs.execute(sql_upd_authors,
                    {'saved_id': saved_id,'be_removed': file_id}
                )
            except apsw.ConstraintError:
                pass         # ignore, author duplication

    with ag.db.conn as conn:
        curs = conn.cursor()
        update_with_saved()
        curs.execute(sql_del, (file_id,))

def delete_file_dir_link(id: int, dir_id: int):
    sql = 'delete from filedir where (file, dir) = (?,?)'
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

def temp_files_dir(dirs: list, checks: dict) -> bool:
    sql_det = (
        "insert into aux(key, val) select 'files_dir', fd.file from filedir fd",
        "join files f on f.id = fd.file",
        "fd.dir in (select val from aux where key = 'dir')",
        "f.how_added = :how_no",
        "insert into aux (key, val) select 'files_dir', f.id from files f",
        "f.id not in (select distinct file from filedir)",
        "where", "and",
    )

    def files_dir() -> tuple[bool, str]:
        to_join = ((0,6,2,), (0,1,6,2,7,3,))
        sql0 = "insert into aux values ('dir', ?)"
        sql1 = (
            "with x(id) as (select id from parentdir where parent = ? "
            "union select t.id from x inner join parentdir t "
            "on t.parent = x.id) select * from x"
        )
        dir_ = set(dirs)
        if checks["sub_dir"]:
            for dd in dirs:
                for s in curs.execute(sql1, dd):
                    dir_.add(s)
        curs.executemany(sql0, dir_)

        return (len(dir_) == 1), ' '.join((sql_det[i] for i in to_join[checks["add_method"]]))

    def files_no_dir() -> str:
        to_join = ((4,6,5,), (4,6,5,7,3,))
        return ' '.join((sql_det[i] for i in to_join[checks["add_method"]]))

    curs = ag.db.conn.cursor()
    ret_val = False
    if checks["dir"]:
        ret_val, sql = files_dir()
    elif checks["no_dir"]:
        sql = files_no_dir()
    elif checks["add_method"]:
        sql = ' '.join((sql_det[i] for i in (4,6,3,)))
    else:
        return False

    if checks["add_method"]:
        curs.execute(sql, {'how_no': checks.get("how_added", 1)})
    else:
        curs.execute(sql)
    return ret_val

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
        'select f.filename, p.path, f.added, f.opened, f.modified, '
        'f.created, f.published, f.nopen, f.rating, f.size, f.pages '
        'from files f join paths p on p.id = f.path where f.id = ?'
    )
    return ag.db.conn.cursor().execute(sql, (id,)).fetchone()

def move_file(new_dir: int, old_dir: int, file_id: int):
    sql ='update filedir set dir = :new where (dir, file) = (:old, :id);'
    with ag.db.conn as conn:
        try:
            conn.cursor().execute(
                sql, {'new': new_dir, 'old': old_dir, 'id': file_id}
            )
        except apsw.ConstraintError:
            pass         # ignore, duplication

def copy_file(file_id: int, dir_id: int):
    sql = 'insert into filedir (file, dir) values (?, ?);'
    with ag.db.conn as conn:
        try:
            conn.cursor().execute(sql, (file_id, dir_id))
        except apsw.ConstraintError:
            pass         # ignore, duplication

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

def get_file_export(fileid: int) -> dict:
    def in_export(sql: str) -> list:
        tt = []
        for cc in cursor.execute(sql, (fileid,)):
            tt.append(cc[0])
        return tt

    sql1 = (
        'select f.hash, f.filename, f.modified, f.opened, '
        'f.created, f.rating, f.nopen, f.size, f.pages, '
        'f.published, p.path from files f join paths p '
        'on p.id = f.path where f.id = ?'
    )
    sql2 = (
        'select t.tag from tags t join filetag f on '
        'f.tagid = t.id where f.fileid = ?'
    )
    sql3 = (
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

        res['tags'] = in_export(sql2)

        res['authors'] = in_export(sql3)

    return res
#endregion

def update_tooltip(data: ag.DirData):
    sql1 = 'select name from dirs where id = ?'
    sql2 = 'update parentdir set tool_tip = ? where (parent, id) = (?,?)'
    with ag.db.conn as conn:
        curs = conn.cursor()
        dir_name = curs.execute(sql1, (data.id,)).fetchone()
        tip = None if dir_name[0] == data.tool_tip else data.tool_tip
        curs.execute(
            sql2, (tip, data.parent_id, data.id)
        )

def update_dir_name(name: str, data: ag.DirData):
    sql1 = 'update dirs set name = ? where id = ?'
    sql2 = 'update parentdir set tool_tip = null where (parent, id) = (?,?)'
    with ag.db.conn as conn:
        conn.cursor().execute(sql1, (name, data.id))
        if name == data.tool_tip:
            conn.cursor().execute(sql2, (data.parent_id, data.id))

def save_file_id(d_data: ag.DirData):
    sql = 'update parentdir set file_id = ? where (parent, id) = (?,?)'

    with ag.db.conn as conn:
        conn.cursor().execute(
            sql, (d_data.file_id, d_data.parent_id, d_data.id)
        )

def insert_dir(dir_name: str, parent: int) -> int:
    sql2 = 'insert into dirs (name) values (?);'
    sql3 = 'insert into parentdir (parent, id, hide, file_id) values (?, ?, 0, 0);'
    with ag.db.conn as conn:
        curs = conn.cursor()
        curs.execute(sql2, (dir_name,))
        id = conn.last_insert_rowid()
        curs.execute(sql3, (parent, id,))
    return id

def update_hidden_state(id: int, parent: int, hidden: bool):
    sql = 'update parentdir set hide = :hide where (id,parent) = (:id,:parent)'
    with ag.db.conn as conn:
        conn.cursor().execute(sql, {'hide':hidden, 'id':id, 'parent':parent})

def dir_parents(dir_id: int) -> apsw.Cursor:
    sql = 'select parent from parentdir where id = ?'
    return ag.db.conn.cursor().execute(sql, (dir_id,))

def not_parent_child(id1, id2) -> bool:
    sql = 'select 1 from parentdir where (parent,id) = (?,?)'
    res = ag.db.conn.cursor().execute(sql, (id1, id2)).fetchone()
    return not res

def dir_min_parent(dir_id: int) -> int:
    sql = 'select parent from parentdir where id = ?'
    parent = ag.db.conn.cursor().execute(sql, (dir_id,)).fetchone()
    return parent[0]

def dir_children(id: int) -> apsw.Cursor:
    sql = 'select parent, id from parentdir where parent = ?'
    with ag.db.conn as conn:
        return conn.cursor().execute(sql, (id,))

def children_names(parent: int) -> apsw.Cursor:
    sql = ('select d.name, d.id, d.multy from dirs d '
          'join parentdir p on d.id = p.id where p.parent = ?;'
    )
    with ag.db.conn as conn:
        return conn.cursor().execute(sql, (parent,))

def get_dir_name(id: int) -> str:
    sql = 'select name from dirs where id = ?'
    res = ag.db.conn.cursor().execute(sql, (id,)).fetchone()
    return res[0] if res else ''

def break_link(folder: int, parent: int) -> int:
    """
    returns number of remaining parents
    """
    sql1 = 'delete from parentdir where (parent, id) = (?,?)'
    sql2 = 'select count(*) from parentdir where id = ?'
    sql3 = 'update dirs set multy = 0 where id = ?'
    sql4 = 'delete from dirs where id = ?'
    with ag.db.conn as conn:
        conn.cursor().execute(sql1, (parent, folder))
        cnt = conn.cursor().execute(sql2, (folder,)).fetchone()[0]
        if cnt == 1:
            conn.cursor().execute(sql3, (folder,))
        if not cnt:
            conn.cursor().execute(sql4, (folder,)).fetchone()
        return cnt

def copy_dir(parent: int, dir_data: ag.DirData) -> bool:
    sql1 = 'update dirs set multy = 1 where id = :id'
    sql2 = 'insert into parentdir (parent, id, hide, file_id) values (:parent, :id, 0, :file_id)'
    with ag.db.conn as conn:
        try:
            conn.cursor().execute(sql1, {'id': dir_data.id,})
            conn.cursor().execute(
                sql2,
                {'parent': parent,
                 'id': dir_data.id,
                 'file_id': dir_data.file_id,}
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
    sql = 'update parentdir set parent = :new where (parent, id) = (:old, :id);'
    with ag.db.conn as conn:
        try:
            conn.cursor().execute(sql, {"id": id, "old": old, "new": new})
            return True
        except apsw.ConstraintError:
            return False   # dir can't be moved here, already exists

def get_file_hash(file_id: int) -> str:
    hash_sql = "select hash from files where id = ? and size > 0"
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
    sql = 'select filenote from filenotes where (fileid, id) = (?,?);'
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

def update_note_exported(fileid: int, noteid: int, note: str) -> int:
    sql1 = ('update filenotes set filenote = :filenote '
        'where (fileid, id) = (:fileid, :id)')

    with ag.db.conn as conn:
        conn.cursor().execute(sql1,
            {
                'fileid': fileid,
                'id': noteid,
                'filenote': note,
            }
        )

def update_note(fileid: int, noteid: int, note: str) -> int:
    sql0 = 'select modified from filenotes where (fileid, id) = (:fileid, :id)'
    sql1 = ('update filenotes set (filenote, modified) = (:filenote, unixepoch()) '
        'where (fileid, id) = (:fileid, :id)')

    file_id = get_file_id_to_notes(fileid)
    with ag.db.conn as conn:
        curs = conn.cursor()
        ts0 = curs.execute(sql0, {'fileid': file_id, 'id': noteid,}).fetchone()
        curs.execute(sql1,
            {
                'fileid': file_id,
                'id': noteid,
                'filenote': note,
            }
        )
        ts = curs.execute(sql0, {'fileid': file_id, 'id': noteid,}).fetchone()

        return ts[0] if ts[0] > ts0[0] else -1

def delete_note(file: int, note: int):
    sql = 'delete from filenotes where (fileid, id) = (?,?);'
    ag.db.conn.cursor().execute(sql, (file, note))

def delete_file_notes(file: int):
    sql_id = 'delete from filenotes where fileid = ?;'
    sql_hash = (
        'delete from filenotes where fileid in '
        '(select id from files where hash = ?);'
    )
    hash_ = get_file_hash(file)
    if hash_:
        ag.db.conn.cursor().execute(sql_hash, (hash_,))
    else:
        ag.db.conn.cursor().execute(sql_id, (file,))

def get_tags() -> apsw.Cursor:
    sql = 'select Tag, ID from Tags order by Tag COLLATE NOCASE;'
    return ag.db.conn.cursor().execute(sql)

def get_file_tagid(file_id: int) -> apsw.Cursor:
    sql = 'select TagID from FileTag where FileID = ?'
    return ag.db.conn.cursor().execute(sql, (file_id,))

def insert_tag(tag: str) -> int:
    sql = "insert into Tags (Tag) values (:tag);"
    ag.db.conn.cursor().execute(sql, {'tag': tag})
    return ag.db.conn.last_insert_rowid()

def insert_file_tag(tag: int, file: int):
    sql = 'insert into filetag (tagid, fileid) values (:tag_id, :file_id);'
    try:
        ag.db.conn.cursor().execute(sql, {'tag_id': tag, 'file_id': file})
    except apsw.ConstraintError:
        pass         # ignore, duplication

def delete_tag_file(tag: int, file: int):
    sql = 'delete from filetag where (tagid, fileid) = (:tag, :file)'
    try:
        ag.db.conn.cursor().execute(sql, {'tag': tag, 'file': file})
    except apsw.ConstraintError:
        pass         # ignore, seems this never happen

def update_tag(id: int, val: str):
    sql = 'update tags set tag = :tag where id = :id'
    with ag.db.conn as conn:
        conn.cursor().execute(sql, {'id': id, 'tag': val})

def detele_tag(id):
    sql = 'delete from tags where id = :id'
    with ag.db.conn as conn:
        conn.cursor().execute(sql, {'id': id})

def get_tag_files(tag: int) -> set[int]:
    sql = 'select fileid from FileTag where tagid = ?'
    curs = ag.db.conn.cursor().execute(sql, (tag,))
    files = []
    for id in curs:
        files.append(id[0])
    return set(files)

def get_note_date_files(checks: dict) -> apsw.Cursor:
    """
    checks['note_date'] — one of the options:
    "last modified", "any modified", "last created", "any created"
    So last_any is last or any; date_field — modified or created
    """
    last_any, date_field = checks['note_date'].split(' ')
    param = {}
    def compose_sql() -> str:
        cond = []
        if checks['after']:
            cond.append(f"{date_field} >= :after")
            param['after'] = checks['date_after']
        if checks['before']:
            cond.append(f"{date_field} <= :before")
            param['before'] = checks['date_before']
        if last_any == "any":
            return f'select distinct fileid from filenotes where {" and ".join(cond)}'
        if last_any == "last":
            return (f'with x(fileid, {date_field}) as '
            f'(select fileid, max({date_field}) from filenotes group by fileid) '
            f'select fileid from x where {" and ".join(cond)}'
        )

    if checks['note date is set']:
        sql = compose_sql()
        return ag.db.conn.cursor().execute(sql, param)
    else:
        return []

def create_connection(path: str) -> bool:
    if not path:
        return False
    try:
        conn: apsw.Connection = apsw.Connection(path)
        ag.db.path = path
        ag.db.conn = conn
    except apsw.CantOpenError as e:
        ag.show_message_box(
            'Error open DB',
            f'{e.args}, DB file: {path}',
            icon=QStyle.StandardPixmap.SP_MessageBoxCritical
        )
        return False

    if not create_db.tune_new_version():
        ag.db.path = ''
        ag.db.conn.close()
        return False

    ag.signals_.user_signal.emit('Enable_buttons')

    cursor = conn.cursor()
    cursor.execute('pragma foreign_keys = ON;')
    cursor.execute('pragma temp_store = MEMORY;')
    cursor.execute('pragma busy_timeout=1000')
    cursor.execute('create temp table if not exists aux (key, val)')
    save_to_temp("TREE_PATH", '')

    return True
