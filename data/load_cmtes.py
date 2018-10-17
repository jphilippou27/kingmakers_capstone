import csv, sqlite3, sys


if __name__ == "__main__":
    filename = ""
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        sys.exit(1)

    conn = sqlite3.connect("os.db")
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS cmtes;")
    conn.commit()
    cur.execute("""CREATE TABLE cmtes (
        cycle TEXT(4), 
        cmte_id TEXT(9), 
        name TEXT(50), 
        affiliate TEXT(50),
        parent TEXT(50), 
        recip_id TEXT(9), 
        recip_code TEXT(2), 
        fec_cand_id TEXT(9), 
        party TEXT(1),
        industry TEXT(5),
        source TEXT(5), 
        sensitive TEXT(1),
        foreign_owner INTEGER,
        active_now INTEGER
        );"""
        )
    conn.commit()

    with open(filename + ".txt", errors="ignore") as input:
        counter = 0
        reader = csv.reader(input, delimiter=",", quotechar="|")
        rows = [(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13]) for row in reader]
    cur.executemany("""INSERT INTO cmtes (
        cycle, 
        cmte_id, 
        name, 
        affiliate,
        parent, 
        recip_id, 
        recip_code, 
        fec_cand_id, 
        party,
        industry,
        source, 
        sensitive,
        foreign_owner,
        active_now
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);""", rows )
    conn.commit()
    conn.close()


            
