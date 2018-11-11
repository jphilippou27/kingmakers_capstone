import csv, sqlite3, sys


if __name__ == "__main__":
    filename = ""
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        sys.exit(1)

    conn = sqlite3.connect("os.db")
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS cands;")
    conn.commit()
    cur.execute("""CREATE TABLE cands (
        cycle TEXT(4), 
        fec_cand_id TEXT(9), 
        cand_id TEXT(9), 
        name TEXT(50), 
        party TEXT(1), 
        sought_office TEXT(4), 
        current_office TEXT(4), 
        curr_cand TEXT(1),
        cycle_cand TEXT(1),
        cpr_ico TEXT(1),
        recip_code TEXT(2),
        no_pacs TEXT(1));"""
        )
    conn.commit()

    with open(filename + ".txt", errors="ignore") as input:
        counter = 0
        reader = csv.reader(input, delimiter=",", quotechar="|")
        rows = [(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11]) for row in reader]
    cur.executemany("""INSERT INTO cands (
        cycle, 
        fec_cand_id, 
        cand_id, 
        name, 
        party, 
        sought_office, 
        current_office, 
        curr_cand,
        cycle_cand,
        cpr_ico,
        recip_code,
        no_pacs
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);""", rows )
    conn.commit()
    conn.close()


            
