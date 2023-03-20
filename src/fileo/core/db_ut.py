from loguru import logger
import apsw
from collections import deque
from pathlib import PurePath

from PyQt6.QtCore import Qt

from . import app_globals as ag, create_db


def dir_tree_select() -> list:
    to_show_hidden = ag.app.show_hidden.checkState() is Qt.CheckState.Checked
    sql2 = ('select p.parent, d.id, p.is_copy, p.hide, d.name '
               'from dirs d join parentdir p on p.id = d.id '
               'where p.parent = :pid',
               'and p.hide = 0')
    sql = sql2[0] if to_show_hidden else ' '.join(sql2)

    curs: apsw.Cursor = ag.db['Conn'].cursor()

    qu = deque()
    qu.append((0, []))

    while qu:
        id, path = qu.pop()
        pp = [*path]
        pp.append(id)
        rows = curs.execute(sql, {'pid': id})
        for row in rows:
            qu.appendleft((row[1], pp))
            key = ','.join([str(p) for p in pp])
            yield key, row[-1], ag.DirData(*row[:-1])

def get_authors() -> apsw.Cursor:
    sql = 'select author, id from authors order by author COLLATE NOCASE;'
    return ag.db['Conn'].cursor().execute(sql)

def get_file_author_id(id: int) -> apsw.Cursor:
    sql = "select aid from fileauthor where fileid = ?"
    return ag.db['Conn'].cursor().execute(sql, (id,))

def get_file_authors(id: int) -> apsw.Cursor:
    sql = (
        'select author from authors a join fileauthor f on f.aid = a.id '
        'where f.fileid = ? order by author COLLATE NOCASE;'
    )
    return ag.db['Conn'].cursor().execute(sql, (id,))

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
    with ag.db['Conn'] as conn:
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
    ag.db['Conn'].cursor().execute(sql, {'a_id': a_id, 'f_id': f_id})

def update_author(id: int, val: str):
    sql = 'update authors set author = :name where id = :id'
    ag.db['Conn'].cursor().execute(sql, {'id': id, 'name': val})

def detele_author(id):
    sql = 'delete from authors where id = :id'
    with ag.db['Conn'] as conn:
        conn.cursor().execute(sql, {'id': id})

def get_ext_list():
    sql = (
        'select extension, id from extensions '
        'order by extension COLLATE NOCASE;'
    )
    return ag.db['Conn'].cursor().execute(sql)

#region files
def get_files(did: int, parent: int):
    sql = (
        'with x(fileid, commented) as (select fileid, max(modified) '
        'from comments group by fileid) '
        'select f.filename, f.opened, f.rating, f.nopen, f.modified, f.pages, '
        'f.size, f.published, COALESCE(x.commented, -62135596800), f.created, '
        'f.id, fd.dir, f.extid, f.path from files f '
        'left join x on x.fileid = f.id '
        'join filedir fd on fd.file = f.id '
        'join parentdir p on fd.dir = p.id '      # to avoid duplications
        'where fd.dir = :id and p.parent = :pid;'
    )
    return ag.db['Conn'].cursor().execute(sql, {'id': did, 'pid': parent})

def lost_files() -> bool:
    """
    put the lost files in a special folder and show it
    """
    sql0 = (
        'insert into filedir select id,1 from files where id '
        'not in (select distinct file from filedir)'
    )
    sql1 = 'select 1 from parentdir where (parent,id) = (0,1)'
    sql2 = 'insert into parentdir values (0, 1, 0, 0)'
    sql3 = 'select file from filedir where dir = 1'
    sql4 = 'delete from parentdir where (parent,id) = (0,1)'
    sql5 = "select 1 from dirs where id = 1"
    sql6 = "insert into dirs values (1, '@@Lost')"
    def hide_lost_dir() -> bool:
        res = conn.cursor().execute(sql3).fetchone()
        if not res:
            conn.cursor().execute(sql4)
        return not res

    def show_lost_dir() -> bool:
        res = conn.cursor().execute(sql1).fetchone()
        if not res:
            conn.cursor().execute(sql2)
        return not res

    try:
        with ag.db['Conn'] as conn:
            id1 = conn.cursor().execute(sql5).fetchone()
            if not id1:
                conn.cursor().execute(sql6).fetchone()

            before = conn.last_insert_rowid()
            conn.cursor().execute(sql0)
            after = conn.last_insert_rowid()

            if after == before:
                return hide_lost_dir()

            return show_lost_dir()
    except:
        return False

def registered_file_id(path: str, filename: str):
    sql = (
        'select f.id from files f join paths p on p.id = f.path '
        'where f.filename = ? and p.path = ?'
    )
    res = ag.db['Conn'].cursor().execute(sql, (filename, path)).fetchone()
    return res[0] if res else 0

def insert_file(file_: list):
    sql = (
        'insert into files (path, extid, hash, filename, '
        'modified, opened, created, rating, nopen, size, '
        'pages, published) values (?,?,?,?,?,?,?,?,?,?,?,?)'
    )

    def get_path_id(conn: apsw.Connection) -> int:
        sql1 = 'select id from paths where path = ?'
        sql2 = 'insert into paths (path) values (?)'
        curs = conn.cursor()
        res = curs.execute(sql1, (file_[-1],)).fetchone()
        if res:
            return res[0]
        curs.execute(sql2, (file_[-1],)).fetchone()
        return conn.last_insert_rowid()

    def get_ext_id(conn: apsw.Connection) -> int:
        sql1 = 'select id from extensions where extension = ?'
        sql2 = 'insert into extensions (extension) values (?)'
        ext = PurePath(file_[1]).suffix.strip('.')
        curs = conn.cursor()
        res = curs.execute(sql1, (ext,)).fetchone()
        if res:
            return res[0]
        curs.execute(sql2, (ext,)).fetchone()
        return conn.last_insert_rowid()

    with ag.db['Conn'] as conn:
        path_id = get_path_id(conn)
        ext_id = get_ext_id(conn)
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
    with ag.db['Conn'] as conn:
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
    with ag.db['Conn'] as conn:
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

def insert_comments(id: int, comments: list):
    """
    id - file id
    """
    sql3 = (
        'insert into comments values (?,?,?,?,?)'
    )

    def get_max_comment_id(cursor: apsw.Cursor) -> int:
        sql = 'select max(id) from comments where fileid = ?'

        tt = cursor.execute(sql, (id,)).fetchone()
        return tt[0] if tt[0] else 0

    def comment_already_exists(cursor: apsw.Cursor, rec: list) -> bool:
        sql = (
            'select 1 from comments where fileid = ? '
            'and created = ? and modified = ?'
        )
        tt = cursor.execute(sql, (id, rec[2], rec[3])).fetchone()
        return bool(tt)

    with ag.db['Conn'] as conn:
        curs = conn.cursor()
        max_comment_id = get_max_comment_id(curs)

        for rec in comments:
            if comment_already_exists(curs, rec):
                continue
            max_comment_id += 1
            curs.execute(sql3, (id, max_comment_id, *rec[1:]))

def recent_loaded_files():
    sql = (
        'select f.id, f.filename, p.path from files f '
        'join paths p on p.id = f.path where f.size = 0'
    )
    return ag.db['Conn'].cursor().execute(sql)

def files_toched(last_scan: int):
    sql = (
        'select f.id, f.filename, p.path, f.hash from files f '
        'join paths p on p.id = f.path where f.opened > ?'
    )
    return ag.db['Conn'].cursor().execute(sql, (last_scan,))

def get_pdf_files():
    sql = (
        "select f.id, f.filename, p.path from files f "
        "join paths p on p.id = f.path "
        "join extensions e on e.id = f.extid "
        "where f.pages = 0 and e.extension = 'pdf'"
    )
    return ag.db['Conn'].cursor().execute(sql)

def update_file_data(id, st, hash):
    sql = (
        'update files set (modified, created, size, hash) '
        '= (?, ?, ?, ?) where id = ?'
    )
    ag.db['Conn'].cursor().execute(
        sql, (int(st.st_mtime), int(st.st_ctime),
        st.st_size, hash, id)
    )

def update_pdf_file(id, pages, p_date):
    sql = (
        'update files set (pages, published) = (?, ?) where id = ?'
    )
    ag.db['Conn'].cursor().execute(sql, (pages, p_date))

def filter_sqls(key: str, field: str='') -> str:
    return {
        'dir_sql': "select distinct val from aux where key = 'files_dir'",
        'tag_sql':(
            "select val from aux where key = 'file_tag'"
        ),
        'ext_sql': (
            "select id from files where extid in "
            "(select val from aux where key = 'ext')"
        ),
        'author_sql': (
            "select fileid from fileauthor where aid in "
            "(select val from aux where key = 'author')"
        ),
        'sql0': (
            'with x(fileid, commented) as (select fileid, max(modified) '
            'from comments group by fileid) '
            'select f.filename, f.opened, f.rating, f.nopen, f.modified, f.pages, '
            'f.size, f.published, COALESCE(x.commented, -62135596800), f.created, '
            'f.id, 0, f.extid, f.path from files f '
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

def filter_files(param: dict) -> apsw.Cursor:
    # print(param)
    sqlist = filter_subsqls(param)

    par, cond = filter_parcond(param)

    sql = assemble_filter_sql(cond, sqlist)

    # print(sql)
    # print(f"{par=}")

    return (
        ag.db['Conn'].cursor().execute(sql, tuple(par))
        if par else ag.db['Conn'].cursor().execute(sql)
    )

def filter_subsqls(param) -> list[str]:
    sqlist = []
    if param['dir']:
        sqlist.append(filter_sqls('dir_sql'))
    if param['tag']:
       sqlist.append(filter_sqls('tag_sql'))
    if param['ext']:
       sqlist.append(filter_sqls('ext_sql'))
    if param['author']:
       sqlist.append(filter_sqls('author_sql'))
    return sqlist

def filter_parcond(param) -> tuple:
    par = []
    cond = []
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
    return par, cond

def assemble_filter_sql(cond, sqlist) -> str:
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

def delete_file(id: int):
    sql = 'delete from files where id = ?'
    ag.db['Conn'].cursor().execute(sql, (id,))

def delete_file_dir_link(id: int, dir_id: int):
    sql = 'delete from filedir where file = ? and dir = ?'
    ag.db['Conn'].cursor().execute(sql, (id, dir_id))

def get_dir_id_for_file(file: int) -> int:
    sql = 'select dir from filedir where file = ?'
    res = ag.db['Conn'].cursor().execute(sql, (file,)).fetchone()
    return res[0] if res else 0

def temp_files_dir():
    sql = (
        "insert into aux(key, val) select 'files_dir', file from "
        "filedir where dir in (select val from aux where key = 'dir')"
    )
    ag.db['Conn'].cursor().execute(sql)

def clear_temp():
    ag.db['Conn'].cursor().execute("delete from aux where key not like 'save%'")

def save_to_temp(key: str, val: int):
    ag.db['Conn'].cursor().execute("insert into aux values (?, ?)", (key, val))

def save_branch_in_temp(path: str):
    sql = 'update aux set val = ? where key = ?'
    ag.db['Conn'].cursor().execute(sql, (path, 'TREE_PATH'))

def get_branch_from_temp() -> str:
    sql = 'select val from aux where key = ?'
    res = ag.db['Conn'].cursor().execute(sql, ('TREE_PATH',)).fetchone()
    return res[0] if res else ''

def get_file_path(id: int) -> str:
    sql = 'select path from paths where id = ?'
    path = ag.db['Conn'].cursor().execute(sql, (id,)).fetchone()
    return path[0] if path else ''

def get_file_info(id: int):
    sql = (
        'select f.filename, p.path, f.opened, f.modified, f.created, '
        'f.published, f.nopen, f.rating, f.size, f.pages from files f '
        'join paths p on p.id = f.path where f.id = ?'
    )
    return ag.db['Conn'].cursor().execute(sql, (id,)).fetchone()

def move_file(new_dir: int, old_dir: int, file: int):
    sql ='update filedir set dir = :new where dir = :old and file = :id;'
    with ag.db['Conn'] as conn:
        try:
            conn.cursor().execute(
                sql, {'new': new_dir, 'old': old_dir, 'id': file}
            )
        except apsw.ConstraintError:
            pass         # re-copy, duplication

def copy_file(id: int, dir: int):
    sql = 'insert into filedir (file, dir) values (?, ?);'
    with ag.db['Conn'] as conn:
        try:
            conn.cursor().execute(sql, (id, dir))
        except apsw.ConstraintError:
            pass         # re-copy, duplication

def update_opened_file(id: int) -> int:
    """
    return new unixepoch timestamp, or -1 if not created
    """
    sql0 = "select opened from files where id = ?"
    sql1 = "update files set (opened, nopen) = (unixepoch(), nopen+1) where id = ?"
    with ag.db['Conn'] as conn:
        curs = conn.cursor()
        ts0 = curs.execute(sql0, (id,)).fetchone()
        curs.execute(sql1, (id,))
        ts = curs.execute(sql0, (id,)).fetchone()
        return ts[0] if ts[0] > ts0[0] else -1

def update_files_field(id: int, field: str, val):
    #  rating, Pages, published
    sql = f'update files set {field} = ? where id = ?'
    with ag.db['Conn'] as conn:
        conn.cursor().execute(sql, (val, id))

def get_export_data(fileid: int):
    sql1 = (
        'select f.hash, f.filename, f.modified, f.opened, '
        'f.created, f.rating, f.nopen, f.size, f.pages, '
        'f.published, p.path from files f join paths p '
        'on p.id = f.path where f.id = ?'
    )
    sql2 = (
        'select id, comment, created, modified '
        'from comments where fileid = ?'
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
    with ag.db['Conn'] as conn:
        cursor = conn.cursor()
        tt = cursor.execute(sql1, (fileid,)).fetchone()
        if not tt:
            return None
        res['file'] = tt

        tt = []
        for cc in cursor.execute(sql2, (fileid,)):
            tt.append(cc)
        res['comments'] = tt

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

def update_dir_name(name: str, id: int):
    sql = 'update dirs set name = ? where id = ?'
    with ag.db['Conn'] as conn:
        conn.cursor().execute(sql, (name, id))

def insert_dir(dir_name: str, parent: int) -> int:
    sql2 = 'insert into dirs (name) values (?);'
    sql3 = 'insert into parentdir values (?, ?, 0, 0);'
    with ag.db['Conn'] as conn:
        curs = conn.cursor()
        curs.execute(sql2, (dir_name,))
        id = conn.last_insert_rowid()
        curs.execute(sql3, (parent, id))
    return id

def copy_existed(file_id: int, parent_dir: int) -> int:
    """
    make copy of existed file while import from file
    """
    sql = (  # the "Existed" folder id in the current folder if any
        'select d.id from dirs d join parentdir p on '
        'p.id = d.id where p.parent = ? and d.name = ?'
    )
    id = ag.db['Conn'].cursor().execute(sql, (parent_dir, 'Existed')).fetchone()
    exist_id = id[0] if id else insert_dir('Existed', parent_dir)
    copy_file(file_id, exist_id)
    return exist_id

def toggle_hidden_dir_state(id: int, parent: int, hidden: bool):
    sql = 'update parentdir set hide = :hide where (id,parent) = (:id,:parent)'
    with ag.db['Conn'] as conn:
        conn.cursor().execute(sql, {'hide':hidden, 'id':id, 'parent':parent})

def dir_children(id: int):
    sql = 'select * from parentdir where parent = ?'
    with ag.db['Conn'] as conn:
        curs = conn.cursor()
        return curs.execute(sql, (id,))

def delete_dir(id: int, parent: int):
    """
    delete dir with all children if any
    """
    sql1 = 'delete from parentdir where id = ?'  # delete copies of this dir
    sql2 = 'delete from dirs where id = ?'       # delete this dir

    with ag.db['Conn'] as conn:
        curs: apsw.Cursor = conn.cursor()
        curs.execute(sql1, (id,))
        curs.execute(sql2, (id,))

def remove_dir_copy(id: int, parent: int):
    sql = 'delete from parentdir where (parent, id) = (?,?)'
    with ag.db['Conn'] as conn:
        conn.cursor().execute(sql, (parent, id))

def copy_dir(parent: int, id: int) -> bool:
    sql = 'insert into parentdir values (?, ?, 1, 0);'
    with ag.db['Conn'] as conn:
        try:
            conn.cursor().execute(sql, (parent, id))
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
    with ag.db['Conn'] as conn:
        try:
            conn.cursor().execute(sql, {"id": id, "old": old, "new": new})
            return True
        except apsw.ConstraintError:
            return False   # dir can't be moved here, already exists

def get_file_notes(file_id: int):
    sql = (
        "select comment, id, modified, created from Comments "
        "where fileID = ? order by modified desc;"
    )
    return ag.db['Conn'].cursor().execute(sql, (file_id,))

def get_note(file: int, note: int) -> str:
    sql = 'select comment from comments where fileid = ? and id = ?;'
    note_text = ag.db['Conn'].cursor().execute(sql, (file, note)).fetchone()
    return '' if (note_text is None) else note_text[0]

def insert_note(fileid: int, note: str) -> int:
    sql1 = 'select max(id) from comments where fileid=?;'
    sql2 = ('insert into comments (fileid, id, comment, modified, '
        'created) values (:fileid, :id, :comment, :modified, :created);')
    with ag.db['Conn'] as conn:
        curs = conn.cursor()
        tmp = curs.execute(sql1, (fileid,)).fetchone()
        id = tmp[0]+1 if tmp[0] else 1
        ts = curs.execute('select unixepoch()').fetchone()
        if not ts:
            return -1
        curs.execute(sql2,
            {
                'fileid': fileid,
                'id': id,
                'comment': note,
                'modified': ts[0],
                'created': ts[0]
            }
        )
        return ts[0]

def update_note(fileid: int, id: int, note: str) -> int:
    sql0 = 'select modified from comments where fileid=:fileid and id=:id'
    sql1 = ('update comments set (comment, modified) = (:comment, unixepoch()) '
        'where fileid=:fileid and id=:id')
    with ag.db['Conn'] as conn:
        curs = conn.cursor()
        ts0 = curs.execute(sql0,{ 'fileid': fileid, 'id': id, }).fetchone()
        curs.execute(sql1,
            {
                'fileid': fileid,
                'id': id,
                'comment': note,
            }
        )
        ts = curs.execute(sql0,{ 'fileid': fileid, 'id': id, }).fetchone()

        return ts[0] if ts[0] > ts0[0] else -1

def delete_note(file: int, note: int):
    sql = 'delete from comments where fileid = ? and id = ?;'
    ag.db['Conn'].cursor().execute(sql, (file, note))

def get_tags():
    sql = 'select Tag, ID from Tags order by Tag COLLATE NOCASE;'
    return ag.db['Conn'].cursor().execute(sql)

def get_file_tags(file_id: int):
    sql = ('select Tag, ID from Tags where ID in '
        '(select TagID from FileTag where FileID = ?);')
    return ag.db['Conn'].cursor().execute(sql, (file_id,))

def get_file_tagid(file_id: int):
    sql = 'select TagID from FileTag where FileID = ?'
    return ag.db['Conn'].cursor().execute(sql, (file_id,))

def insert_tag(tag: str) -> int:
    sql = "insert into Tags (Tag) values (:tag);"
    ag.db['Conn'].cursor().execute(sql, {'tag': tag})
    return ag.db['Conn'].last_insert_rowid()

def insert_tag_file(tag: int, file: int):
    sql = 'insert into filetag (tagid, fileid) values (:tag_id, :file_id);'
    try:
        ag.db['Conn'].cursor().execute(sql, {'tag_id': tag, 'file_id': file})
    except apsw.ConstraintError:
        pass

def delete_tag_file(tag: int, file: int):
    sql = 'delete from filetag where (tagid, fileid) = (:tag, :file)'
    try:
        ag.db['Conn'].cursor().execute(sql, {'tag': tag, 'file': file})
    except apsw.ConstraintError:
        pass

def update_file_tag_links(file: int, tags: list[int]):
    """
    only the deletion of file-tag links is done here
    the links addition is already done when the tags list was being prepared
    """
    sql1 = 'select tagid from filetag where fileid = ?'
    sql2 = 'delete from filetag where (tagid, fileid) = (:tag, :file)'
    with ag.db['Conn'] as conn:
        curs1: apsw.Cursor = conn.cursor()
        curs2: apsw.Cursor = conn.cursor()
        old_tags = curs1.execute(sql1, (file,))
        for tag in old_tags:
            if tag[0] in tags:
                continue
            curs2.execute(sql2, {'tag': tag[0], 'file': file})

def update_tag(id: int, val: str):
    sql = 'update tags set tag = :tag where id = :id'
    with ag.db['Conn'] as conn:
        conn.cursor().execute(sql, {'id': id, 'tag': val})

def detele_tag(id):
    sql = 'delete from tags where id = :id'
    with ag.db['Conn'] as conn:
        conn.cursor().execute(sql, {'id': id})

def get_files_tag(tag: int) -> set[int]:
    sql = 'select fileid from FileTag where tagid = ?'
    curs = ag.db['Conn'].cursor().execute(sql, (tag,))
    files = []
    for id in curs:
        files.append(id[0])
    return set(files)

def create_connection(path: str) -> bool:
    print(f"create_connection: {path=}, {ag.db['Path']=}")
    if not path:
        return False

    if not create_db.adjust_user_schema(path):
        return False

    conn: apsw.Connection = apsw.Connection(path)
    ag.db['Path'] = path
    ag.db['Conn'] = conn

    cursor = conn.cursor()
    cursor.execute('pragma foreign_keys = ON;')
    cursor.execute('pragma temp_store = MEMORY;')
    cursor.execute('pragma busy_timeout=1000')

    cursor.execute('create temp table if not exists aux (key, val)')
    save_to_temp("TREE_PATH", '')

    return True