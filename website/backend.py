import sqlite3
from flask import Flask
from flask import g

app = Flask(__name__)
DATABASE = "/home/dbalck/KingMakers/data/os.db"

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        print("connecting to db.")
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = make_dicts
    return db

@app.teardown_appcontext
def clost_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        print("disconnecting to db.")
        db.Close()

def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value) for idx, value in enumerate(row))

def query_db(query, args=(), one=False):
    cur = get_db().cursor()
    cur.execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def get_expends(trans_id):
    row = query_db("select * from expends where trans_id = ?", [trans_id], one=True)
    return row

def get_candidate(cand_id):
    row = query_db("select * from cands where cand_id = ?", [cand_id], one=True)
    return row

def get_cands_by_name(ln="", fn=""):
    if not ln and not fn:
        return None
    if ln and fn:
        return query_db("select * from cands where name like ?", [fn + "%" + ln])
    elif ln and not fn:
        return query_db("select * from cands where name like ?", ["%" + ln + "%"])
    elif not ln and fn:
        return query_db("select * from cands where name like ?", ["%" + fn + "%"])
    return None

def get_expends_by_amt(min=0, max=0):
    if not min and not max:
        return None
    if min and max:
        return query_db("select * from expends where amount >= ? and amount <= ? order by amount desc limit 1000", [min, max])
    elif min and not max:
        return query_db("select * from expends where amount >= ? order by amount asc limit 1000", [min])
    elif not min and max:
        return query_db("select * from expends where amount <= ? order by amount desc limit 1000", [max])
    return None

