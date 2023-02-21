import pymysql.cursors
import datetime as dt
from config import DB_CONFIG

def mysql_connect(func):
    def wrapper(*args, **kwargs):
        conn = pymysql.connect(**eval(DB_CONFIG))
        try:
            with conn.cursor() as cursor:
                return func(conn=conn, cursor=cursor, *args, **kwargs)
        except pymysql.err.OperationalError:
            pass
        finally:
            conn.close()
    return wrapper


# REGISTRATION
@mysql_connect
def register(conn, cursor, user_id):
    if user_id < 0:
        return
    result = cursor.execute(f"SELECT * FROM users WHERE user_id={user_id}")
    if result == 0:
        cursor.execute(f"INSERT INTO users(user_id, nick, status, partner, preds) "
                       f"values({user_id}, '', 0 , '', 0)")
        conn.commit()


@mysql_connect
def remove_from_db(conn, cursor, user_id):
    result = cursor.execute(f"SELECT * FROM users WHERE user_id={user_id}")
    if result == 1:
        cursor.execute(f"DELETE FROM users WHERE user_id={user_id}")
        conn.commit()


@mysql_connect
def users(conn, cursor):
    res = cursor.execute(f"SELECT user_id FROM users")
    array = list()
    for i in range(0, res):
        row = cursor.fetchone()
        array.append(row[0])
    return array


# STATUSES
@mysql_connect
def check_status(conn, cursor, user_id):
    result = cursor.execute(f"SELECT * FROM users WHERE user_id={user_id}")
    if result == 1:
        cursor.execute(f"SELECT status FROM users WHERE user_id={user_id}")
        return cursor.fetchone()[0]


@mysql_connect
def statuses(conn, cursor):
    users = cursor.execute(f"SELECT user_id, status FROM users")
    array = dict()
    for user in range(0, users):
        row = cursor.fetchone()
        array[row[0]] = row[1]
    return array


@mysql_connect
def set_status(conn, cursor, user_id, status):
    if status > 5:
        status = 5
    result = cursor.execute(f"SELECT * FROM users WHERE user_id={user_id}")
    if result != 1:
        register(user_id)
    cursor.execute(f"UPDATE users SET status={status} WHERE user_id={user_id}")
    conn.commit()


# NICKNAMES
@mysql_connect
def check_nick(conn, cursor, user_id):
    result = cursor.execute(f"SELECT * FROM users WHERE user_id='{user_id}'")
    if result == 1:
        cursor.execute(f"SELECT nick FROM users WHERE user_id='{user_id}'")
        return cursor.fetchone()[0]


@mysql_connect
def nicks(conn, cursor):
    users = cursor.execute(f"SELECT user_id, nick FROM users")
    array = dict()
    for user in range(0, users):
        row = cursor.fetchone()
        array[row[0]] = row[1]
    return array


@mysql_connect
def set_nick(conn, cursor, user_id, nick):
    result = cursor.execute(f"SELECT * FROM users WHERE user_id={user_id}")
    if result == 1:
        nickname = f"[id{user_id}|{nick}]"
        cursor.execute(f"UPDATE users SET nick='{nickname}' WHERE user_id={user_id}")
        conn.commit()
    else:
        register(user_id=user_id)


# PREDS
@mysql_connect
def check_preds(conn, cursor, user_id):
    result = cursor.execute(f"SELECT * FROM users WHERE user_id={user_id}")
    if result == 1:
        cursor.execute(f"SELECT preds FROM users WHERE user_id={user_id}")
        return cursor.fetchone()[0]


@mysql_connect
def preds(conn, cursor):
    users = cursor.execute(f"SELECT user_id, preds FROM users")
    array = dict()
    for user in range(0, users):
        row = cursor.fetchone()
        array[row[0]] = row[1]
    return array


@mysql_connect
def add_pred(conn, cursor, user_id):
    result = cursor.execute(f"SELECT * FROM users WHERE user_id={user_id}")
    pr = 0
    if result == 1:
        pr = check_preds(user_id=user_id)
    else:
        register(user_id=user_id)
    cursor.execute(f"UPDATE users SET preds='{pr + 1}' WHERE user_id={user_id}")
    conn.commit()


@mysql_connect
def remove_pred_db(conn, cursor, user_id):
    result = cursor.execute(f"SELECT * FROM users WHERE user_id={user_id}")
    if result == 1:
        cursor.execute(f"UPDATE users SET preds='{check_preds(user_id=user_id) - 1}' WHERE user_id={user_id}")
        conn.commit()
    else:
        register(user_id=user_id)


@mysql_connect
def marry(conn, cursor, user_id1, user_id2):
    time = dt.datetime.now().strftime("%d.%m.%Y")
    for user_id in [user_id1, user_id2]:
        result = cursor.execute(f"SELECT * FROM users WHERE user_id={user_id}")
        if result == 1:
            cursor.execute(f"UPDATE users SET partner='{user_id1}_{user_id2}_{time}' WHERE user_id={user_id}")
            conn.commit()
        else:
            register(user_id=user_id)


@mysql_connect
def divorce(conn, cursor, user_id):
    marriage = check_marriage(user_id=user_id)
    result = cursor.execute(f"SELECT * FROM users WHERE user_id={user_id}")
    if result == 1:
        cursor.execute(f"UPDATE users SET partner='' WHERE user_id='{marriage.split('_')[0]}'")
        cursor.execute(f"UPDATE users SET partner='' WHERE user_id='{marriage.split('_')[1]}'")
        conn.commit()
    else:
        register(user_id=user_id)


@mysql_connect
def check_marriages(conn, cursor):
    marriages = set()
    result = cursor.execute(f"SELECT partner FROM users")
    for i in range(0, result):
        marriage = cursor.fetchone()[0]
        if marriage != '':
            marriages.add(marriage)
    return marriages


@mysql_connect
def check_marriage(conn, cursor, user_id):
    cursor.execute(f"SELECT partner FROM users WHERE user_id='{user_id}'")
    marriage = cursor.fetchone()[0]
    return marriage
