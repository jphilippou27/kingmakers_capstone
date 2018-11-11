
USE_POSTGRES=True

if not USE_POSTGRES:
    import sqlite3
if USE_POSTGRES:
    import psycopg2
from flask import Flask
from flask import g

app = Flask(__name__)
DATABASE = "/home/daniel/kingmakers_capstone/data/os.db"
CONNECTION_STR = "/var/www/production/connection_str"
ROOT_CERT = "/var/www/production/root.crt"

if not USE_POSTGRES:
    def get_db():
        db = getattr(g, '_database', None)
        if db is None:
            print("connecting to db.")
            db = g._database = sqlite3.connect(DATABASE)
            db.row_factory = make_dicts
        return db
if USE_POSTGRES:
    def get_db():
        db = getattr(g, '_database', None)
        if db is None:
            with open(CONNECTION_STR, 'r') as f:
                conx = f.read().strip()
            print("connecting to postgres...")
            db = g._database = psycopg2.connect(conx, sslrootcert=ROOT_CERT)
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

def get_cands_by_amt():
    return query_db("select recip_id, sum(amount) as amt, cands.name from indivs join cands where cands.cand_id = indivs.recip_id group by recip_id order by amt desc limit 10", [])


######
        
def get_all_sums_by_cand():
    return query_db("select sum(amount) as amt, indivs.recip_id, cands.name from indivs join cands where cands.cand_id = indivs.recip_id group by indivs.recip_id order by amt desc limit 100", [])
def get_all_sums_by_cmte():
    return query_db("select sum(amount) as amt, indivs.recip_id, cmtes.name from indivs join cmtes where cmtes.cmte_id = indivs.recip_id group by indivs.recip_id order by amt desc limit 100", [])
def get_all_sums_by_industry():
    return query_db("select sum(amount) as amt, indivs.industry, industry.name from indivs join industry on indivs.industry = industry.code  group by indivs.industry order by amt desc limit 100", [])

def get_income_by_cand():
    return query_db("select sum(amount) as amt, indivs.recip_id, cands.name from indivs join cands where cands.cand_id = indivs.recip_id group by indivs.recip_id order by amt desc limit 100", [])
def get_income_by_cmte():
    return query_db("select sum(amount) as amt, indivs.recip_id, cmtes.name from indivs join cmtes where cmtes.cmte_id = indivs.recip_id group by indivs.recip_id order by amt desc limit 100", [])
def get_income_by_industry():
    pass

def get_spending_by_cand():
    pass
def get_spending_by_cmte():
    rows = query_db("select sum(amt) as total, id, name from (select sum(amount) as amt, pacs2cands.pac_id as id, cmtes.name as name from pacs2cands join cmtes on pacs2cands.pac_id = cmtes.cmte_id group by pac_id UNION ALL select sum(amount) as amt, pacs2pacs.filer_id as id, cmtes.name as name from pacs2pacs join cmtes on pacs2pacs.filer_id = cmtes.cmte_id group by filer_id order by amt desc ) group by id order by total desc limit 100", [])

def get_spending_by_industry():
    return query_db("select sum(amt) as total, industry, name from (select sum(amount) as amt, pacs2cands.industry as industry, industry.name as name from pacs2cands join industry on pacs2cands.industry = industry.code group by industry.code UNION ALL select sum(amount) as amt, pacs2pacs.donor_industry as industry, industry.name as name from pacs2pacs join industry on pacs2pacs.donor_industry = industry.code group by industry order by amt desc ) group by  industry order by total desc limit 100", [])


def get_sankey_by_industry():
     return query_db("select donor_industry as src, recip_industry as tgt, sum(amount) as amt from pacs2pacs group by donor_industry, recip_industry union all  select industry || '_2' as src, cand_id as tgt, sum(amount) as amt from pacs2cands group by industry, cand_id  order by amt desc limit 100", [])

#def get_simple_sankey_by_industry():
#     return query_db("select cmtes.name as source, cands.name as target, sum(p2c.amount) as value from pacs2cands as p2c join cmtes on cmtes.cmte_id = p2c.pac_id join cands on cands.cand_id = p2c.cand_id group by p2c.pac_id order by value desc limit 10", [])
     
 
def get_simple_sankey_by_industry():
     return query_db("select MAX(industry.name) as source, MAX(cands.name) as target, sum(amount) as value, substr(industry,0,2) from pacs2cands join industry on pacs2cands.industry = industry.code join cands on pacs2cands.cand_id = cands.cand_id  where substr(industry.code,0,2) != 'J' AND substr(industry.code,0,2) != 'Z' group by industry, pacs2cands.cand_id order by value desc limit 50", [])
