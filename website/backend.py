
USE_POSTGRES=False

import sqlite3
import psycopg2 
import psycopg2.extras
from flask import Flask
from flask import g
import numpy as np
import pandas as pd

app = Flask(__name__)
SQLITE = "/home/dbalck/kingmakers_capstone/data/os2/os2.db"
CONNECTION_STR = "/var/www/production/connection_str"
ROOT_CERT = "/var/www/production/root.crt"

def get_sqlite():
    db = getattr(g, '_database', None)
    if db is None:
        print("connecting to db.")
        db = g._database = sqlite3.connect(SQLITE)
        db.row_factory = make_dicts
    return db

def get_pg():
    db = getattr(g, '_database', None)
    if db is None:
        with open(CONNECTION_STR, 'r') as f:
            conx = f.read().strip()
        print("connecting to postgres...")
        db = g._database = psycopg2.connect(conx,
                                            sslrootcert=ROOT_CERT,
                                            cursor_factory=psycopg2.extras.RealDictCursor)
    return db            

@app.teardown_appcontext
def clost_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        print("disconnecting to db.")
        db.Close()

def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value) for idx, value in enumerate(row))

def query_pg(query, args=(), one=False):
    cur = get_pg().cursor()
    cur.execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def query_sqlite(query, args=(), one=False):
    cur = get_sqlite().cursor()
    cur.execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def get_expends(trans_id):
    row = query_sqlite("select * from expends where trans_id = ?", [trans_id], one=True)
    return row

def get_candidate(cand_id):
    row = query_sqlite("select * from cand where id = ?", [cand_id], one=True)
    return row

def get_against_candidate_time_series(cand_id):
    return query_sqlite("select date, sum(amount) as amount from pac2cand where trans_type = ? and cand_id = ? group by date asc", ["24A", cand_id], one=False)

def get_cands_by_name(ln="", fn=""):
    if not ln and not fn:
        return None
    if ln and fn:
        return query_sqlite("select * from cands where name like ?", [fn + "%" + ln])
    elif ln and not fn:
        return query_sqlite("select * from cands where name like ?", ["%" + ln + "%"])
    elif not ln and fn:
        return query_sqlite("select * from cands where name like ?", ["%" + fn + "%"])
    return None

def get_expends_by_amt(min=0, max=0):
    if not min and not max:
        return None
    if min and max:
        return query_sqlite("select * from expends where amount >= ? and amount <= ? order by amount desc limit 1000", [min, max])
    elif min and not max:
        return query_sqlite("select * from expends where amount >= ? order by amount asc limit 1000", [min])
    elif not min and max:
        return query_sqlite("select * from expends where amount <= ? order by amount desc limit 1000", [max])
    return None

def get_cands_by_amt():
    return query_sqlite("select recip_id, sum(amount) as amt, cands.name from indivs join cands where cands.cand_id = indivs.recip_id group by recip_id order by amt desc limit 10", [])


######
        
def get_all_sums_by_cand():
    return query_sqlite("select sum(amount) as amt, indivs.recip_id, cands.name from indivs join cands where cands.cand_id = indivs.recip_id group by indivs.recip_id order by amt desc limit 100", [])
def get_all_sums_by_cmte():
    return query_sqlite("select sum(amount) as amt, indivs.recip_id, cmtes.name from indivs join cmtes where cmtes.cmte_id = indivs.recip_id group by indivs.recip_id order by amt desc limit 100", [])
def get_all_sums_by_industry():
    return query_sqlite("select sum(amount) as amt, indivs.industry, industry.name from indivs join industry on indivs.industry = industry.code  group by indivs.industry order by amt desc limit 100", [])

def get_income_by_cand():
    return query_sqlite("select sum(amount) as amt, indivs.recip_id, cands.name from indivs join cands where cands.cand_id = indivs.recip_id group by indivs.recip_id order by amt desc limit 100", [])
def get_income_by_cmte():
    return query_sqlite("select sum(amount) as amt, indivs.recip_id, cmtes.name from indivs join cmtes where cmtes.cmte_id = indivs.recip_id group by indivs.recip_id order by amt desc limit 100", [])

def interest_spending_for(cand_id):
    return query_sqlite("select interest.name as interest, sum(amount) as total from cmte2cand join cmte_advanced on cmte_advanced.id = cmte2cand.filer_id join interest on interest.code = cmte_advanced.interest where cmte2cand.cand_id = ? and trans_type != '24A' group by interest order by total desc", [cand_id])

def industry_spending_against():
    pass

def spenders_for_cand(cand_id):
    return query_sqlite("select cmte.name as spender, sum(amount) as total from cmte2cand join cmte on cmte.id = cmte2cand.filer_id where cmte2cand.cand_id = ? and trans_type != '24A' group by filer_id order by total desc", [cand_id])

def independent_spenders_against_cand(cand_id):
    return query_sqlite("select cmte.name as spender, sum(amount) as total from cmte2cand join cmte on cmte.id = cmte2cand.filer_id where cmte2cand.cand_id = ? and trans_type = '24A' group by filer_id order by total desc", [cand_id])

def cmte_timeseries_against(cand_id):
    return query_sqlite("select strftime('%Y-%m', date) as date, sum(amount) as total from cmte2cand where cmte2cand.cand_id = ? and trans_type = '24A' group by strftime('%Y-%m', date) order by strftime('%Y-%m', date) desc", [cand_id])

def cmte_timeseries_for(cand_id):
    return query_sqlite("select strftime('%Y-%m', date) as date, sum(amount) as total from cmte2cand where cmte2cand.cand_id = ? and trans_type != '24A' group by strftime('%Y-%m', date) order by strftime('%Y-%m', date) desc", [cand_id])

def get_spending_by_cmte():
    rows = query_sqlite("select sum(amt) as total, id, name from (select sum(amount) as amt, pacs2cands.pac_id as id, cmtes.name as name from pacs2cands join cmtes on pacs2cands.pac_id = cmtes.cmte_id group by pac_id UNION ALL select sum(amount) as amt, pacs2pacs.filer_id as id, cmtes.name as name from pacs2pacs join cmtes on pacs2pacs.filer_id = cmtes.cmte_id group by filer_id order by amt desc ) group by id order by total desc limit 100", [])

def get_spending_by_industry():
    return query_sqlite("select sum(amt) as total, industry, name from (select sum(amount) as amt, pacs2cands.industry as industry, industry.name as name from pacs2cands join industry on pacs2cands.industry = industry.code group by industry.code UNION ALL select sum(amount) as amt, pacs2pacs.donor_industry as industry, industry.name as name from pacs2pacs join industry on pacs2pacs.donor_industry = industry.code group by industry order by amt desc ) group by  industry order by total desc limit 100", [])
 
def get_simple_sankey_by_industry():
    return query_sqlite("select source, target, value, party from (select interest.name as source, cand.name as target, sum(amount) as value, cand.party as party from cmte2cand join cmte_advanced on cmte_advanced.id = cmte2cand.filer_id join interest on interest.code = cmte_advanced.interest join cand on cand.id = cmte2cand.cand_id where trans_type != '24A' and substr(cmte_advanced.interest, 0, 2) != 'J' and substr(cmte_advanced.interest, 0, 2) != 'Z' group by cmte_advanced.interest, cmte2cand.cand_id order by value desc) where value > 200000")
     #return query_sqlite("""select MAX(interest.name) as source, MAX(cands.name) as target, sum(amount) as value, substr(interest,0,1) from cmte2cand join interest on cmte2cand.industry = industry.code join cands on pacs2cands.cand_id = cands.cand_id  where substr(industry.code,0,2) != 'J' AND substr(industry.code,0,2) != 'Z' group by industry, pacs2cands.cand_id order by value desc limit 50""", [])

def cand_lookup(name):
    res = query_sqlite("select name, id from cand where name like ?", ["%" + name + "%"])
    return res

def make_links(dataset):
    """Create source and link pairs for the network graph from a pandas dataframe
    
    'INPUT: aggregated pandas dataframe with these columns:  sum(amount) ,feccandid, bioguide_id, firstlastp, party, Industry
    'OUTPUT: JSON format of links (ex: {"value": 20000.0, "source": 1, "target": 96},
    """
    
    #create a list of target and source values
    links_list = list(dataset.apply(lambda row: {"source": row['industry'], "target": row['firstlastp'], "value": row['contr_amt']}, axis=1))
    #print(links_list)
    #make an index of the values
    unique_ids = pd.Index(dataset['industry']
                      .append(dataset['firstlastp'])
                      .reset_index(drop=True).unique())
    #print(unique_ids)
    #convert source and target values to numbers for d3.v3
    links_list_fv = []
    for link in links_list:
        record = {"value":link['value'], "source": (unique_ids.get_loc(link['source'])+1),
         "target": (unique_ids.get_loc(link['target'])+1)}
        links_list_fv.append(record)
    return (links_list)

def make_nodes(dataset):
    """Create nodes for the network graph from a pandas dataframe
    
    'INPUT: aggregated pandas dataframe with these columns:  sum(amount) ,feccandid, bioguide_id, firstlastp, party, Industry
    'OUTPUT: JSON format of links (ex: {'name': 'Misc Agriculture', 'group': 'Industry', 'pic_id': 'flower'},
    """
    #contributions nodes
    df_nodes_I = pd.DataFrame(dataset.industry.unique())
    df_nodes_I["party"] = "Industry"
    df_nodes_I['bioguide_id'] = 'flower'
    df_nodes_I.columns = ['firstlastp' if x== 0 else x for x in df_nodes_I.columns]
    df_nodes_I.head()
    
    #same thing for politicians
    df_nodes_P = dataset[['firstlastp', 'party', 'bioguide_id']].drop_duplicates()
    df_nodes_P.head()
    
    #merge nodes
    df_nodes = pd.concat([df_nodes_I, df_nodes_P])
    
    #Convert to list
    node_list = list(df_nodes.apply(lambda row: {"name": row['firstlastp'], "group": row['party'], "pic_id": row['bioguide_id']}, axis=1))
    
    #export
    return(node_list)
def merge_nodes_links(links_list_fv, node_list):
     #merge
    json_prep = {"nodes":node_list, "links":links_list_fv}
    json_prep.keys()
    
    #convert to json
    import json
    json_dump = json.dumps(json_prep, indent=1)
    return(json_dump)

def get_network_by_industry(firstlastp):
    cand = ("'"+ str(firstlastp) +"'")
    row = query_pg(f"SELECT * FROM network_industry t1 LEFT JOIN (select distinct(Industry) FROM network_industry WHERE firstlastp = {cand})sub ON t1.Industry = sub.Industry WHERE (sub.Industry IS NOT NULL) and (t1.contr_amt> 1)", [])
    df_network_viz_fv = pd.DataFrame([i.copy() for i in row])
    links_list_fv = make_links(df_network_viz_fv)
    node_list = make_nodes(df_network_viz_fv)
    network_json = merge_nodes_links(links_list_fv, node_list)
    
    return (network_json)

def get_individual_support_direct(cand_id):
    limit = 10
    return query_pg("SELECT indivs.contribid AS indivs_contribid, indivs.contrib AS donor_name, SUM(indivs.amount) AS total_amt FROM pq_crp_indivs18 indivs WHERE indivs.recipid = ? GROUP BY indivs_contribid, donor_name ORDER BY total_amt DESC LIMIT ?", [cand_id, limit])

def get_waterfall_data(cand_id):
    result_set = query_pg(f"select 'Independent Spending Against' as group, -1 * sum(transaction_amt) as amt from itoth18 where other_id = '{cand_id}' and transaction_tp = '24A' union select 'Independent Spending For' as group, sum(transaction_amt) as amt from itoth18 where other_id = '{cand_id}' and transaction_tp = '24E' union select 'Individual Contributions' as group, sum(transaction_amt) as amt from itcont18 where cmte_id in (select cmte_id from pacs_related where cand_id = '{cand_id}') and transaction_tp similar to '(10|15|15E)' union select 'Contributions by Candidate' as group, sum(transaction_amt) as amt from itcont18 where cmte_id in (select cmte_id from pacs_related where cand_id = '{cand_id}') and transaction_tp = '15C';")
    return result_set


def get_candidate_tree(cand_id):
    result_set = query_pg(f"select 'Large PAC Contributors' as source, cmte_nm as target, sum(total) as value from pacs_large where cmte_id in  (select cmte_id from pacs_related where cand_id = '{cand_id}') group by cmte_id, cmte_nm having sum(total) > 10000 union select 'Medium PAC Contributors' as source, cmte_nm as target, sum(total) as value from pacs_medium where cmte_id in  (select cmte_id from pacs_related where cand_id = '{cand_id}') group by cmte_id, cmte_nm having sum(total) > 10000 union select 'Small PAC Contributors' as source, cmte_nm as target, sum(total) as value from pacs_small where cmte_id in  (select cmte_id from pacs_related where cand_id = '{cand_id}') group by cmte_id, cmte_nm having sum(total) > 10000 union select 'Individual Contributors' as source, cmte_nm as target, sum(total) as value from indivs_simple where cmte_id in  (select cmte_id from pacs_related where cand_id = '{cand_id}') group by cmte_id, cmte_nm having sum(total) > 10000 union select y.cmte_nm as source, z.cmte_nm as target, sum(x.transaction_amt) as value from itoth18 x inner join cm18 y on y.cmte_id = x.cmte_id inner join cm18 z on z.cmte_id = x.other_id where x.other_id in ( select cmte_id from pacs_related where cand_id = '{cand_id}') and x.transaction_tp = '24G' group by y.cmte_nm, z.cmte_nm having sum(x.transaction_amt) > 10000 union select 'Super PACs' as source, z.cand_name as target, sum(x.transaction_amt) as value from itoth18 x join cn18 z on z.cand_id = x.other_id where x.other_id = '{cand_id}' and x.transaction_tp = '24E' group by z.cand_name having sum(x.transaction_amt) > 10000")
    return result_set

def get_industries_by_party():
    # return query_pg("select industry as source, party as target, sum(total) as value from interest_spending group by industry, party order by value desc limit 50;" )
    return query_pg("select industry as source, party as target, sum(total) as value from interest_spending where industry in (select industry as total from interest_spending group by industry order by sum(total) desc limit 50) group by industry, party having sum(total) > 500000000" )


