import csv, sqlite3, sys


if __name__ == "__main__":
    filename = ""
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        sys.exit(1)

    conn = sqlite3.connect("os.db")
    cur = conn.cursor()
    # 23 columns
    cur.execute("DROP TABLE IF EXISTS indivs;")
    conn.commit()
    cur.execute("""CREATE TABLE indivs (
        cycle TEXT(4), 
        fec_trans_id TEXT(19), 
        contrib_id TEXT(12), 
        name TEXT(50), 
        recip_id TEXT(9), 
        org TEXT(50), 
        parent_org TEXT(50), 
        industry TEXT(5),
        date TEXT(12),
        amount INT,
        street TEXT(40),
        city TEXT(30),
        state TEXT(2),
        zip TEXT(5),
        recip_code TEXT(2),
        trans_type TEXT(3),
        committee_id TEXT(9),
        other_id TEXT(9),
        gender TEXT(1),
        microfilm TEXT(11),
        occupation TEXT(38),
        employer TEXT(38),
        source TEXT(5)
        );"""
        )
    conn.commit()

    with open(filename + ".txt", errors="ignore") as input:
        counter = 0
        reader = csv.reader(input, delimiter=",", quotechar="|")
        rows = [(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18], row[19], row[20], row[21], row[22] ) for row in reader]
    
    # 23 columns
    cur.executemany("""INSERT INTO indivs (
        cycle, 
        fec_trans_id, 
        contrib_id, 
        name, 
        recip_id, 
        org, 
        parent_org, 
        industry,
        date,
        amount,
        street,
        city,
        state,
        zip,
        recip_code,
        trans_type,
        committee_id,
        other_id,
        gender,
        microfilm,
        occupation,
        employer,
        source
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);""", rows )
    conn.commit()
    conn.close()


            
