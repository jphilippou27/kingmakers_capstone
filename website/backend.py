USE_POSTGRES=False

import sqlite3
import psycopg2
import psycopg2.extras
from flask import Flask
from flask import g
import numpy as np
import pandas as pd

app = Flask(__name__)
CONNECTION_STR = "/var/www/production/connection_str"
ROOT_CERT = "/var/www/production/root.crt"
#db = None

def get_pg():
    if not hasattr(g, 'db'):
        with open(CONNECTION_STR, 'r') as f:
            conx = f.read().strip()
        print("connecting to postgres...")
        g.db = psycopg2.connect(conx,
                                            sslrootcert=ROOT_CERT,
                                            cursor_factory=psycopg2.extras.RealDictCursor)
    return g.db

@app.teardown_appcontext
def close_connection(exception):
    db = g.pop('db', None)
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

# def query_pg(query, args=(), one=False):
#     cur = get_sqlite().cursor()
#     cur.execute(query, args)
#     rv = cur.fetchall()
#     cur.close()
#     return (rv[0] if rv else None) if one else rv

def get_expends(trans_id):
    row = query_pg("select * from expends where trans_id = %s",(trans_id,), one=True)
    return row

def get_candidate(cand_id):
    row = query_pg("select * from cn18 where cand_id = %s", (cand_id,), one=True)
    return row

def get_all_cands():
    return query_pg("select cand_id, cand_name from cn18")

def get_against_candidate_time_series(cand_id):
    return query_pg("select date, sum(amount) as amount from pac2cand where trans_type = %s and cand_id = %s group by date asc", ("24A", cand_id), one=False)

def get_cands_by_name(ln="", fn=""):
    if not ln and not fn:
        return None
    if ln and fn:
        return query_pg("select * from cands where name like %s", [fn + "%" + ln])
    elif ln and not fn:
        return query_pg("select * from cands where name like %s", ("%" + ln + "%",))
    elif not ln and fn:
        return query_pg("select * from cands where name like %s", ("%" + fn + "%"))
    return None

def get_expends_by_amt(min=0, max=0):
    if not min and not max:
        return None
    if min and max:
        return query_pg("select * from expends where amount >= %s and amount <= %s order by amount desc limit 1000", (min, max))
    elif min and not max:
        return query_pg("select * from expends where amount >= %s order by amount asc limit 1000", (min,))
    elif not min and max:
        return query_pg("select * from expends where amount <= %s order by amount desc limit 1000", (max,))
    return None

def get_cands_by_amt():
    return query_pg("select recip_id, sum(amount) as amt, cands.name from indivs join cands where cands.cand_id = indivs.recip_id group by recip_id order by amt desc limit 10")


######

def get_all_sums_by_cand():
    return query_pg("select sum(amount) as amt, indivs.recip_id, cands.name from indivs join cands where cands.cand_id = indivs.recip_id group by indivs.recip_id order by amt desc limit 100")
def get_all_sums_by_cmte():
    return query_pg("select sum(amount) as amt, indivs.recip_id, cmtes.name from indivs join cmtes where cmtes.cmte_id = indivs.recip_id group by indivs.recip_id order by amt desc limit 100")
def get_all_sums_by_industry():
    return query_pg("select sum(amount) as amt, indivs.industry, industry.name from indivs join industry on indivs.industry = industry.code  group by indivs.industry order by amt desc limit 100")

def get_income_by_cand():
    return query_pg("select sum(amount) as amt, indivs.recip_id, cands.name from indivs join cands where cands.cand_id = indivs.recip_id group by indivs.recip_id order by amt desc limit 100")
def get_income_by_cmte():
    return query_pg("select sum(amount) as amt, indivs.recip_id, cmtes.name from indivs join cmtes where cmtes.cmte_id = indivs.recip_id group by indivs.recip_id order by amt desc limit 100")

def interest_spending_for(cand_id):
    return query_pg("select interest.name as interest, sum(amount) as total from cmte2cand join cmte_advanced on cmte_advanced.id = cmte2cand.filer_id join interest on interest.code = cmte_advanced.interest where cmte2cand.cand_id = %s and trans_type != '24A' group by interest order by total desc", (cand_id,))

def industry_spending_against():
    pass

def spenders_for_cand(cand_id):
    return query_pg("select cmte.name as spender, sum(amount) as total from cmte2cand join cmte on cmte.id = cmte2cand.filer_id where cmte2cand.cand_id = %s and trans_type != '24A' group by filer_id order by total desc", (cand_id,))

def independent_spenders_against_cand(cand_id):
    return query_pg("select cmte.name as spender, sum(amount) as total from cmte2cand join cmte on cmte.id = cmte2cand.filer_id where cmte2cand.cand_id = %s and trans_type = '24A' group by filer_id order by total desc", (cand_id,))

def cmte_timeseries_against(cand_id):
    return query_pg("select to_char(to_date(x.transaction_dt, 'MMDDYYYY'), 'YYYY-MM') as date, sum(x.transaction_amt) as total from itpas218 x where x.cand_id = %s and x.transaction_tp = '24A' group by to_char(to_date(x.transaction_dt, 'MMDDYYYY'), 'YYYY-MM') having to_char(to_date(x.transaction_dt, 'MMDDYYYY'), 'YYYY-MM') is not null order by to_char(to_date(x.transaction_dt, 'MMDDYYYY'), 'YYYY-MM') desc ; ", [cand_id])

def cmte_timeseries_for(cand_id):
    return query_pg("select to_char(to_date(x.transaction_dt, 'MMDDYYYY'), 'YYYY-MM') as date, sum(x.transaction_amt) as total from itpas218 x where x.cand_id = %s and x.transaction_tp similar to '24(K|E)' group by to_char(to_date(x.transaction_dt, 'MMDDYYYY'), 'YYYY-MM') having to_char(to_date(x.transaction_dt, 'MMDDYYYY'), 'YYYY-MM') is not null order by to_char(to_date(x.transaction_dt, 'MMDDYYYY'), 'YYYY-MM') desc ; ", [cand_id])
    # return query_pg("select to_date(transaction_dt, 'MMDDYYYY') as date, sum(transaction_amt) as total from itpas218 x where x.cand_id = %s and transaction_tp != '24A' group by to_date(transaction_dt, 'MMDDYYYY') order by to_date(transaction_dt, 'MMDDYYYY') desc", [cand_id])

def get_spending_by_cmte():
    rows = query_pg("select sum(amt) as total, id, name from (select sum(amount) as amt, pacs2cands.pac_id as id, cmtes.name as name from pacs2cands join cmtes on pacs2cands.pac_id = cmtes.cmte_id group by pac_id UNION ALL select sum(amount) as amt, pacs2pacs.filer_id as id, cmtes.name as name from pacs2pacs join cmtes on pacs2pacs.filer_id = cmtes.cmte_id group by filer_id order by amt desc ) group by id order by total desc limit 100")

def get_spending_by_industry():
    return query_pg("select sum(amt) as total, industry, name from (select sum(amount) as amt, pacs2cands.industry as industry, industry.name as name from pacs2cands join industry on pacs2cands.industry = industry.code group by industry.code UNION ALL select sum(amount) as amt, pacs2pacs.donor_industry as industry, industry.name as name from pacs2pacs join industry on pacs2pacs.donor_industry = industry.code group by industry order by amt desc ) group by  industry order by total desc limit 100")

def get_simple_sankey_by_industry():
    return query_pg("select source, target, value, party from (select interest.name as source, cand.name as target, sum(amount) as value, cand.party as party from cmte2cand join cmte_advanced on cmte_advanced.id = cmte2cand.filer_id join interest on interest.code = cmte_advanced.interest join cand on cand.id = cmte2cand.cand_id where trans_type != '24A' and substr(cmte_advanced.interest, 0, 2) != 'J' and substr(cmte_advanced.interest, 0, 2) != 'Z' group by cmte_advanced.interest, cmte2cand.cand_id order by value desc) where value > 200000")
     #return query_pg("""select MAX(interest.name) as source, MAX(cands.name) as target, sum(amount) as value, substr(interest,0,1) from cmte2cand join interest on cmte2cand.industry = industry.code join cands on pacs2cands.cand_id = cands.cand_id  where substr(industry.code,0,2) != 'J' AND substr(industry.code,0,2) != 'Z' group by industry, pacs2cands.cand_id order by value desc limit 50""", ])

def cand_lookup(name):
    res = query_pg("select cand_name as name, cand_id as id from cn18 where cand_name ilike %s;", ['%' + name + '%'])# , ("%" + name + "%")
    print(res)
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
    df_nodes_I = pd.DataFrame(dataset.groupby(['industry'], as_index = False)['contr_amt'].sum())
    df_nodes_I["party"] = "Industry"
    df_nodes_I['ge_winner_ind_guess'] = "NotApplicable"
    df_nodes_I = df_nodes_I.rename(index=str, columns={"industry": "firstlastp", " contr_amt": " contr_amt", "party":"party", "ge_winner_ind_guess":"ge_winner_ind_guess" })
    #['firstlastp' if x == 0 else x for x in df_nodes_I.columns]
    print(df_nodes_I.head())

    #same thing for politicians
    df_nodes_P = pd.DataFrame(dataset.groupby(['firstlastp','party','ge_winner_ind_guess'], as_index = False)['contr_amt'].sum())
    #df_nodes_P.head()

    #merge nodes
    df_nodes = pd.concat([df_nodes_I, df_nodes_P])

    #Convert to list
    node_list = list(df_nodes.apply(lambda row: {"name": row['firstlastp'], "group": row['party'],  "contribution_total": row['contr_amt'], "winner_ind":row['ge_winner_ind_guess']}, axis=1))

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
    cand = (str(firstlastp))
    min_contribution = 150000
    row = query_pg("SELECT * FROM network_industry t1 RIGHT JOIN (select distinct(industry) FROM network_industry \
                    WHERE (firstlastp = %s and contr_amt > 75000)) sub ON t1.industry = sub.industry  \
                        WHERE (sub.industry IS NOT NULL) and (t1.contr_amt> 75000)", [cand])
    # print(row)
    print("sql draw", cand)
    df_network_viz_fv = pd.DataFrame([i.copy() for i in row])
    links_list_fv = make_links(df_network_viz_fv)
    node_list = make_nodes(df_network_viz_fv)
    network_json = merge_nodes_links(links_list_fv, node_list)

    return (network_json)

def make_links_indivd(dataset):
    """Create source and link pairs for the network graph from a pandas dataframe

    'INPUT: aggregated pandas dataframe with these columns:  sum(amount) ,feccandid, bioguide_id, firstlastp, party, Industry
    'OUTPUT: JSON format of links (ex: {"value": 20000.0, "source": 1, "target": 96},
    """

    #create a list of target and source values
    links_list = list(dataset.apply(lambda row: {"source": row['contrib'], "target": row['firstlastp'], "value": row['contr_amt']}, axis=1))
    #print(links_list)
    #make an index of the values
    unique_ids = pd.Index(dataset['contrib']
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

def make_nodes_individ(dataset):
    """Create nodes for the network graph from a pandas dataframe

    'INPUT: aggregated pandas dataframe with these columns:  sum(amount) ,feccandid, bioguide_id, firstlastp, party, Industry
    'OUTPUT: JSON format of links (ex: {'name': 'Misc Agriculture', 'group': 'Industry', 'pic_id': 'flower'},
    """
    #contributions nodes
    df_nodes_I = pd.DataFrame(dataset.groupby(['contrib'], as_index = False)['contr_amt'].sum())
    df_nodes_I["party"] = "Contributor"
    df_nodes_I['ge_winner_ind_guess'] = "NotApplicable"
    df_nodes_I = df_nodes_I.rename(index=str, columns={"contrib": "firstlastp", " contr_amt": " contr_amt", "party":"party", "ge_winner_ind_guess":"ge_winner_ind_guess" })
    #['firstlastp' if x == 0 else x for x in df_nodes_I.columns]
    print(df_nodes_I.head())

    #same thing for politicians
    df_nodes_P = pd.DataFrame(dataset.groupby(['firstlastp','party','ge_winner_ind_guess'], as_index = False)['contr_amt'].sum())
    #df_nodes_P.head()

    #merge nodes
    df_nodes = pd.concat([df_nodes_I, df_nodes_P])

    #Convert to list
    node_list = list(df_nodes.apply(lambda row: {"name": row['firstlastp'], "group": row['party'],  "contribution_total": row['contr_amt'], "winner_ind":row['ge_winner_ind_guess']}, axis=1))

    #export
    return(node_list)

def get_network_individ(firstlastp):
    cand = (str(firstlastp))
    print("sql qc: ", cand)
    row = query_pg("SELECT * FROM network_individ t2 RIGHT JOIN(SELECT Distinct(contrib) FROM network_individ \
                         WHERE (firstlastp = %s and contr_amt >1) GROUP BY contrib)sub ON t2.contrib = sub.contrib WHERE \
                        contr_amt >15", [cand]) #might change to db/pg depending on where you are looking at this
    row = pd.DataFrame([i.copy() for i in row])
    links_list_fv = make_links_indivd(row)
    node_list = make_nodes_individ(row)
    json_dump = merge_nodes_links(links_list_fv, node_list)
    #json_dump = json.dumps(network_json, indent=1)
    #node_list = pd.DataFrame([i.copy() for i in row])
    return (json_dump)

def make_links_commit(dataset):
    """Create source and link pairs for the network graph from a pandas dataframe

    'INPUT: aggregated pandas dataframe with these columns:  sum(amount) ,feccandid, bioguide_id, firstlastp, party, Industry
    'OUTPUT: JSON format of links (ex: {"value": 20000.0, "source": 1, "target": 96},
    """

    #create a list of target and source values
    links_list = list(dataset.apply(lambda row: {"source": row['pacshort'], "target": row['firstlastp'], "value": row['contr_amt']}, axis=1))
    #print(links_list)
    #make an index of the values
    unique_ids = pd.Index(dataset['pacshort']
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

def make_nodes_commit(dataset):
    """Create nodes for the network graph from a pandas dataframe

    'INPUT: aggregated pandas dataframe with these columns:  sum(amount) ,feccandid, bioguide_id, firstlastp, party, Industry
    'OUTPUT: JSON format of links (ex: {'name': 'Misc Agriculture', 'group': 'Industry', 'pic_id': 'flower'},
    """
    #contributions nodes
    df_nodes_I = pd.DataFrame(dataset.groupby(['pacshort'], as_index = False)['contr_amt'].sum())
    df_nodes_I["party"] = "Contributor"
    df_nodes_I['ge_winner_ind_guess'] = "Not Applicable"
    df_nodes_I = df_nodes_I.rename(index=str, columns={"pacshort": "firstlastp", " contr_amt": " contr_amt",  "party":"party", "ge_winner_ind_guess":"ge_winner_ind_guess" })
    #['firstlastp' if x == 0 else x for x in df_nodes_I.columns]
    print(df_nodes_I.head())

    #same thing for politicians
    df_nodes_P = pd.DataFrame(dataset.groupby(['firstlastp','party','ge_winner_ind_guess'], as_index = False)['contr_amt'].sum())
    df_nodes_P['type'] = "Not Applicable"
    #df_nodes_P.head()

    #merge nodes
    df_nodes = pd.concat([df_nodes_I, df_nodes_P])

    #Convert to list
    node_list = list(df_nodes.apply(lambda row: {"name": row['firstlastp'], "group": row['party'],  "contribution_total": row['contr_amt'], "winner_ind":row['ge_winner_ind_guess']}, axis=1))

    #export
    return(node_list)

def get_network_committee (firstlastp):
    cand = (str(firstlastp))
    print("committee sql qc: ", cand)
    row = query_pg("Select * FROM committee_network t1 \
                        RIGHT JOIN (select distinct (pacshort)  \
                                    FROM committee_network \
                                    WHERE firstlastp = %s and contr_amt > 2000 \
                                    GROUP BY pacshort)sub \
                    ON t1.pacshort = sub.pacshort \
                   WHERE contr_amt > 2000", [cand])
    row = pd.DataFrame([i.copy() for i in row])
    links_list_fv = make_links_commit(row)
    node_list = make_nodes_commit(row)
    json_dump = merge_nodes_links(links_list_fv, node_list)
    return (json_dump)

def get_network_node_list():
    import json
    row = query_pg("SELECT DISTINCT(firstlastp) FROM network_industry WHERE contr_amt>75000 GROUP BY firstlastp")
    json_dump = json.dumps(row, indent=1)
    #node_list = pd.DataFrame([i.copy() for i in row])
    return (json_dump)

def get_individual_support_direct(cand_id):
    limit = 10
    return query_pg("SELECT indivs.contribid AS indivs_contribid, indivs.contrib AS donor_name, SUM(indivs.amount) AS total_amt FROM pq_crp_indivs18 indivs WHERE indivs.recipid = %s GROUP BY indivs_contribid, donor_name ORDER BY total_amt DESC LIMIT %s", (cand_id, limit))

def get_waterfall_data(cand_id):
    result_set = query_pg("select 'Independent Spending Against' as group, -1 * sum(transaction_amt) as amt from itoth18 where other_id = %s and transaction_tp = '24A' union select 'Independent Spending For' as group, sum(transaction_amt) as amt from itoth18 where other_id = %s and transaction_tp = '24E' union select 'Individual Contributions' as group, sum(transaction_amt) as amt from itcont18 where cmte_id in (select cmte_id from pacs_related where cand_id = %s) and transaction_tp similar to '(10|15|15E)' union select 'Contributions by Candidate' as group, sum(transaction_amt) as amt from itcont18 where cmte_id in (select cmte_id from pacs_related where cand_id = %s) and transaction_tp = '15C';", (cand_id, cand_id, cand_id, cand_id))
    return result_set


def get_candidate_tree(cand_id):
    result_set = query_pg("select 'Large PAC Contributors' as source, cmte_nm as target, sum(total) as value from pacs_large where cmte_id in  (select cmte_id from pacs_related where cand_id = %s) group by cmte_id, cmte_nm having sum(total) > 10000 union select 'Medium PAC Contributors' as source, cmte_nm as target, sum(total) as value from pacs_medium where cmte_id in  (select cmte_id from pacs_related where cand_id = %s) group by cmte_id, cmte_nm having sum(total) > 10000 union select 'Small PAC Contributors' as source, cmte_nm as target, sum(total) as value from pacs_small where cmte_id in  (select cmte_id from pacs_related where cand_id = %s) group by cmte_id, cmte_nm having sum(total) > 10000 union select 'Individual Contributors' as source, cmte_nm as target, sum(total) as value from indivs_simple where cmte_id in  (select cmte_id from pacs_related where cand_id = %s) group by cmte_id, cmte_nm having sum(total) > 10000 union select y.cmte_nm as source, z.cmte_nm as target, sum(x.transaction_amt) as value from itoth18 x inner join cm18 y on y.cmte_id = x.cmte_id inner join cm18 z on z.cmte_id = x.other_id where x.other_id in ( select cmte_id from pacs_related where cand_id = %s) and x.transaction_tp = '24G' group by y.cmte_nm, z.cmte_nm having sum(x.transaction_amt) > 10000 union select 'Super PACs' as source, z.cand_name as target, sum(x.transaction_amt) as value from itoth18 x join cn18 z on z.cand_id = x.other_id where x.other_id = %s and x.transaction_tp = '24E' group by z.cand_name having sum(x.transaction_amt) > 10000", (cand_id, cand_id, cand_id, cand_id, cand_id, cand_id))
    return result_set

def get_candidate_industry_tree(cand_id):
    result_set = query_pg("select industry as source, recip_cmte_nm as target, sum(total) as value from interest_spending_cand_cmtes where cand_id = %s group by industry, party , recip_cmte_nm having sum(total) > 0 union select y.cmte_nm as source, z.cmte_nm as target, sum(x.transaction_amt) as value from itoth18 x inner join cm18 y on y.cmte_id = x.cmte_id inner join cm18 z on z.cmte_id = x.other_id where x.other_id in ( select cmte_id from pacs_related where cand_id = %s) and x.transaction_tp similar to '24G' group by y.cmte_nm, z.cmte_nm having sum(x.transaction_amt) > 10000 limit 80;", [cand_id, cand_id])
    return result_set

def get_industries_by_party():
    return query_pg("select x.industry as source, x.party as target, x.party as party, sum(total) as value, y.proportion as proportion from interest_spending x join (select b.industry, cast(sum(b.total) as decimal) / a.grand_total as proportion from interest_spending b join (select industry, sum(total) as grand_total from interest_spending  group by industry) a on a.industry = b.industry where party = 'Democratic' group by b.industry, a.grand_total) y  on x.industry = y.industry where x.industry in (select industry as total from interest_spending group by industry order by sum(total) desc limit 50)  group by x.industry, x.party, y.proportion having sum(total) > 1000000 order by value desc limit 100;" )

def get_industry_partycands(industryname, partyname):
    # print(industryname, partyname)
    return query_pg("select x.industry as source, x.cand_name as target, x.party, x.cand_id, y.proportion as proportion, sum(x.total) as value from interest_cand_spending x join (select b.industry, cast(sum(b.total) as decimal) / a.grand_total as proportion from interest_spending b join (select industry, sum(total) as grand_total from interest_spending  group by industry) a on a.industry = b.industry where party = 'Democratic' group by b.industry, a.grand_total) y  on x.industry = y.industry where x.industry = %s and x.party = %s group by x.industry, x.cand_name, x.party, x.cand_id, y.proportion order by value desc limit 100", [industryname, partyname])

def get_industry_cands(industryname):
    # print(industryname, partyname)
    return query_pg("select x.industry as source, x.cand_name as target, x.party, y.proportion as proportion, sum(x.total) as value from interest_cand_spending x join (select b.industry, cast(sum(b.total) as decimal) / a.grand_total as proportion from interest_spending b join (select industry, sum(total) as grand_total from interest_spending  group by industry) a on a.industry = b.industry where party = 'Democratic' group by b.industry, a.grand_total) y  on x.industry = y.industry where x.industry = %s group by x.industry, x.cand_name, x.party, y.proportion order by sum(x.total) desc limit 60", [industryname])

def get_superpac_sankey():
    return query_pg("select rank_filter.donor as source, 'For' as type, rank_filter.cmte_nm as target, null as party, rank_filter.total_donation as value from (select donor, cmte_nm, total_donation, rank() over (partition by donor order by total_donation desc) from superpac_donors where donor in (select donor from superpac_donors group by donor order by sum(total_donation) desc limit 50)) rank_filter where rank <= 3 union select rf.cmte_nm as source, 'For' as type, rf.cand_nm as target, z.cand_pty_affiliation as party, rf.total as value from (select cmte_nm, cand_nm, total, rank() over (partition by cmte_nm order by total desc) from superpac_spending where cmte_nm in ( select rank_filter.cmte_nm from (select donor, cmte_nm, total_donation, rank() over (partition by donor order by total_donation desc) from superpac_donors where donor in (select donor from superpac_donors group by donor order by sum(total_donation) desc limit 50)) rank_filter where rank <= 5)) rf join cn18 z on z.cand_name ilike rf.cand_nm  where rank <= 3 union select rf.cmte_nm as source, 'Against' as type, rf.cand_nm as target, z.cand_pty_affiliation as party, rf.total as value from (select cmte_nm, cand_nm, total, rank() over (partition by cmte_nm order by total desc) from superpac_spending_against where cmte_nm in ( select rank_filter.cmte_nm from (select donor, cmte_nm, total_donation, rank() over (partition by donor order by total_donation desc) from superpac_donors where donor in (select donor from superpac_donors group by donor order by sum(total_donation) desc limit 50)) rank_filter where rank <= 5)) rf join cn18 z on z.cand_name ilike rf.cand_nm  where rank <= 3;")

def get_superpac_cand_data(superpac):
    return query_pg("select x.cmte_nm as source, x.cand_id, x.cand_nm as target, y.cand_pty_affiliation as party, sum(x.total) as value from superpac_spending x join cn18 y on y.cand_id = x.cand_id where x.cmte_nm ilike %s group by x.cmte_nm, x.cand_id, x.cand_nm, y.cand_pty_affiliation order by sum(x.total) desc limit 80", [superpac])

def get_cands_per_industry(industry):
    return query_pg("select industry as source, cand_name as target, party, sum(total) as value from interest_cand_spending where industry = %s group by industry, cand_name, party order by value desc limit 60", [industryname])

def get_cand_photo(cand_id):
    try:
      bioguide_id = query_pg("select bioguide_id from pic_ids where FECCandID=%s",
[cand_id], one=True)['bioguide_id'] + '.jpg'
    except:
        bioguide_id = 'could-not-find-pic.png'
    baseurl = r'https://s3.us-south.objectstorage.softlayer.net/staticassets2/'
    return baseurl + bioguide_id

def get_most_recent_election(cand_id):
    s = '''
SELECT * FROM public.election_ppts3 e
LEFT JOIN pic_ids p
ON e.fec_id = p.feccandid
WHERE e.cycle IN (
   SELECT cycle_mr
   FROM public.election_ppts3
   WHERE fec_id='{fec_id}'
)
AND e.district IN (
    SELECT district_mr
    FROM public.election_ppts3
    WHERE fec_id='{fec_id}'
)
AND e.state IN (
    SELECT state_mr
    FROM public.election_ppts3
    WHERE fec_id='{fec_id}'
)
'''.format(fec_id=cand_id)
    return query_pg(s)
