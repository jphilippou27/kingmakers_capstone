import csv, sqlite3, sys


if __name__ == "__main__":
    filename = ""
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        sys.exit(1)

    conn = sqlite3.connect("os.db")
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS expends")
    conn.commit()
    cur.execute("""CREATE TABLE expends (
        cycle TEXT(4), 
        id INT, 
        trans_id TEXT(20), 
        filer_id TEXT(9), 
        recip_code TEXT(2), 
        pac_name TEXT(50), 
        recip_name TEXT(90),
        exp_code TEXT(3),
        amount REAL,
        date TEXT(12),
        city TEXT(30),
        state TEXT(2),
        zip TEXT(5),
        alt_cmte_id TEXT(9),
        cand_id TEXT(9),
        trans_type TEXT(3),
        description TEXT(100),
        pg TEXT(5),
        pg_other TEXT(20),
        recip_type TEXT(3),
        source TEXT(5)
        );"""
        )
    conn.commit()

    rows = []
    counter = 0
    with open(filename + ".txt", errors="ignore") as input:
        reader = csv.reader(input, delimiter=",", quotechar="|")
        for row in reader:
            counter += 1
            rows.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18], row[19], row[20]))
            if counter % 1000000 == 0:
                cur.executemany("""INSERT INTO expends (
                    cycle, 
                    id, 
                    trans_id, 
                    filer_id, 
                    recip_code, 
                    pac_name, 
                    recip_name,
                    exp_code,
                    amount,
                    date,
                    city,
                    state,
                    zip,
                    alt_cmte_id,
                    cand_id,
                    trans_type,
                    description,
                    pg,
                    pg_other,
                    recip_type,
                    source
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);""", rows )
                conn.commit()
                rows = []
    cur.executemany("""INSERT INTO expends (
        cycle, 
        id, 
        trans_id, 
        filer_id, 
        recip_code, 
        pac_name, 
        recip_name,
        exp_code,
        amount,
        date,
        city,
        state,
        zip,
        alt_cmte_id,
        cand_id,
        trans_type,
        description,
        pg,
        pg_other,
        recip_type,
        source
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);""", rows )
    conn.commit()
    conn.close()


            
