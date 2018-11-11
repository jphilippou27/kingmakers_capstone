import csv, sqlite3, sys


if __name__ == "__main__":
    filename = ""
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        sys.exit(1)

    conn = sqlite3.connect("os.db")
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS pacs2cands")
    conn.commit()
    cur.execute("""CREATE TABLE pacs2cands (
        cycle TEXT(4), 
        fec_rec_id TEXT(19), 
        pac_id TEXT(9), 
        cand_id TEXT(9), 
        amount INT,
        date TEXT(12), 
        industry TEXT(5), 
        trans_type TEXT(3), 
        contrib_type TEXT(1),
        fec_cand_id TEXT(9));"""
        )
    conn.commit()

    with open(filename + ".txt", errors="ignore") as input:
        counter = 0
        reader = csv.reader(input, delimiter=",", quotechar="|")
        rows = [(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9]) for row in reader]
    cur.executemany("""INSERT INTO pacs2cands (
        cycle, 
        fec_rec_id, 
        pac_id, 
        cand_id, 
        amount, 
        date, 
        industry,
        trans_type,
        contrib_type,
        fec_cand_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);""", rows )
    conn.commit()
    conn.close()


            
