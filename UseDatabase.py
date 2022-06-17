import pymysql.cursors
import datetime as dt
from config import dbconfig


#REGISTRATION
def register(user_id):
    if user_id < 0:
        return
    conn = pymysql.connect(**dbconfig)
    try:
        with conn.cursor() as cursor:
            result = cursor.execute(f"SELECT * FROM users WHERE user_id={user_id}")
            if result == 0:
                cursor.execute(f"INSERT INTO users(user_id, nick, status, partner, preds) values({user_id}, '', 0 , '', 0)")
                conn.commit()
    except pymysql.err.OperationalError:
        pass
    finally:
        conn.close()


def remove_from_db(user_id):
    conn = pymysql.connect(**dbconfig)
    try:
        with conn.cursor() as cursor:
            result = cursor.execute(f"SELECT * FROM users WHERE user_id={user_id}")
            if result == 1:
                cursor.execute(f"DELETE FROM users WHERE user_id={user_id}")
                conn.commit()
    except pymysql.err.OperationalError:
        pass
    finally:
        conn.close()


#STATUSES
def check_status(user_id):
    conn = pymysql.connect(**dbconfig)
    try:
        with conn.cursor() as cursor:
            result = cursor.execute(f"SELECT * FROM users WHERE user_id={user_id}")
            if result == 1:
                cursor.execute(f"SELECT status FROM users WHERE user_id={user_id}")
                return cursor.fetchone()[0]
    except pymysql.err.OperationalError:
        pass
    finally:
        conn.close()


def statuses():
    conn = pymysql.connect(**dbconfig)
    try:
        with conn.cursor() as cursor:
            users = cursor.execute(f"SELECT user_id, status FROM users")
            array = dict()
            for user in range(0, users):
                row = cursor.fetchone()
                array[row[0]] = row[1]
            return array
    except pymysql.err.OperationalError:
        pass
    finally:
        conn.close()


def set_status(user_id, status):
    if status > 5:
        status = 5
    conn = pymysql.connect(**dbconfig)
    try:
        with conn.cursor() as cursor:
            result = cursor.execute(f"SELECT * FROM users WHERE user_id={user_id}")
            if result == 1:
                cursor.execute(f"UPDATE users SET status={status} WHERE user_id={user_id}")
                conn.commit()
            else:
                register(user_id)
    except pymysql.err.OperationalError:
        pass
    finally:
        conn.close()


#NICKNAMES
def check_nick(user_id):
    conn = pymysql.connect(**dbconfig)
    try:
        with conn.cursor() as cursor:
            result = cursor.execute(f"SELECT * FROM users WHERE user_id='{user_id}'")
            if result == 1:
                cursor.execute(f"SELECT nick FROM users WHERE user_id='{user_id}'")
                return cursor.fetchone()[0]
    except pymysql.err.OperationalError:
        pass
    finally:
        conn.close()


def nicks():
    conn = pymysql.connect(**dbconfig)
    try:
        with conn.cursor() as cursor:
            users = cursor.execute(f"SELECT user_id, nick FROM users")
            array = dict()
            for user in range(0, users):
                row = cursor.fetchone()
                array[row[0]] = row[1]
            return array
    except pymysql.err.OperationalError:
        pass
    finally:
        conn.close()


def set_nick(user_id, nick):
    conn = pymysql.connect(**dbconfig)
    try:
        with conn.cursor() as cursor:
            result = cursor.execute(f"SELECT * FROM users WHERE user_id={user_id}")
            if result == 1:
                nickname = f"[id{user_id}|{nick}]"
                cursor.execute(f"UPDATE users SET nick='{nickname}' WHERE user_id={user_id}")
                conn.commit()
            else:
                register(user_id)
    except pymysql.err.OperationalError:
        pass
    finally:
        conn.close()


#PREDS
def check_preds(user_id):
    conn = pymysql.connect(**dbconfig)
    try:
        with conn.cursor() as cursor:
            result = cursor.execute(f"SELECT * FROM users WHERE user_id={user_id}")
            if result == 1:
                cursor.execute(f"SELECT preds FROM users WHERE user_id={user_id}")
                return cursor.fetchone()[0]                    
    except pymysql.err.OperationalError:
        pass
    finally:
        conn.close()


def preds():
    conn = pymysql.connect(**dbconfig)
    try:
        with conn.cursor() as cursor:
            users = cursor.execute(f"SELECT user_id, preds FROM users")
            array = dict()
            for user in range(0, users):
                row = cursor.fetchone()
                array[row[0]] = row[1]
            return array
    except pymysql.err.OperationalError:
        pass
    finally:
        conn.close()


def add_pred(user_id):
    conn = pymysql.connect(**dbconfig)
    try:
        with conn.cursor() as cursor:
            result = cursor.execute(f"SELECT * FROM users WHERE user_id={user_id}")
            if result == 1:
                pr = check_preds(user_id)
                if pr == None:
                    pr = 0
                cursor.execute(f"UPDATE users SET preds='{pr + 1}' WHERE user_id={user_id}")
                conn.commit()
            else:
                register(user_id)
                cursor.execute(f"UPDATE users SET preds='{pr + 1}' WHERE user_id={user_id}")
                conn.commit()
    except pymysql.err.OperationalError:
        pass
    finally:
        conn.close()


def remove_pred(user_id):
    conn = pymysql.connect(**dbconfig)
    try:
        with conn.cursor() as cursor:
            result = cursor.execute(f"SELECT * FROM users WHERE user_id={user_id}")
            if result == 1:
                cursor.execute(f"UPDATE users SET preds='{check_preds(user_id) - 1}' WHERE user_id={user_id}")
                conn.commit()
            else:
                register(user_id)
    except pymysql.err.OperationalError:
        pass
    finally:
        conn.close()


def marry(user_id1, user_id2):
    conn = pymysql.connect(**dbconfig)
    time = dt.datetime.now().strftime("%d.%m.%Y")
    try:
        with conn.cursor() as cursor:
            result = cursor.execute(f"SELECT * FROM users WHERE user_id={user_id1}")
            if result == 1:
                cursor.execute(f"UPDATE users SET partner='{user_id1}_{user_id2}_{time}' WHERE user_id={user_id1}")
                conn.commit()
            else:
                register(user_id1)
                
            result = cursor.execute(f"SELECT * FROM users WHERE user_id={user_id2}")
            if result == 1:
                cursor.execute(f"UPDATE users SET partner='{user_id1}_{user_id2}_{time}' WHERE user_id={user_id2}")
                conn.commit()
            else:
                register(user_id2)
    except pymysql.err.OperationalError:
        pass
    finally:
        conn.close()


def divorce(user_id):
    conn = pymysql.connect(**dbconfig)
    try:
        with conn.cursor() as cursor:
            marriage = check_marriage(user_id)
            result = cursor.execute(f"SELECT * FROM users WHERE user_id={user_id}")
            if result == 1:
                cursor.execute(f"UPDATE users SET partner='' WHERE user_id='{marriage.split('_')[0]}'")
                cursor.execute(f"UPDATE users SET partner='' WHERE user_id='{marriage.split('_')[1]}'")
                conn.commit()
            else:
                register(user_id)
            
    except pymysql.err.OperationalError:
        pass
    finally:
        conn.close()


def check_marriages():
    conn = pymysql.connect(**dbconfig)
    marriages = set()
    try:
        with conn.cursor() as cursor:
            i = 0
            result = cursor.execute(f"SELECT partner FROM users")
            for i in range(0, result):
                marriage = cursor.fetchone()[0]
                if marriage != '':
                    marriages.add(marriage)
            conn.commit()
            return marriages
    except pymysql.err.OperationalError:
        pass
    finally:
        conn.close()


def check_marriage(user_id):
    conn = pymysql.connect(**dbconfig)
    marriages = set()
    try:
        with conn.cursor() as cursor:
            result = cursor.execute(f"SELECT partner FROM users WHERE user_id='{user_id}'")
            marriage = cursor.fetchone()[0]
            conn.commit()
            return marriage
    except pymysql.err.OperationalError:
        pass
    finally:
        conn.close()
