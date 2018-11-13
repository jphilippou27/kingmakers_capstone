import csv, sqlite3, sys, os


if __name__ == "__main__":
    conn = sqlite3.connect("os2.db")
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS cand")
    conn.commit()
    cur.execute("""CREATE TABLE cand (
        id TEXT(9),
        name TEXT(200),
        incumbent_challenger TEXT(1),
        party TEXT(3),
        total_receipts INTEGER,
        from_auth_cmte INTEGER,
        to_auth_cmte INTEGER,
        total_disbursed INTEGER,
        year TEXT(4),
        state TEXT(2),
        office TEXT(1),
        district TEXT(2),
        status TEXT(1),
        pac TEXT(9));"""
        )
    conn.commit()

    with open("candidates.txt", errors="ignore") as input:
        counter = 0
        reader = csv.reader(input, delimiter="|")
        rows = [(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9] ) for row in reader]
        cur.executemany("""INSERT INTO cand (
            id,
            name,
            party,
            year,
            state,
            office,
            district,
            incumbent_challenger,
            status,
            pac 
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);""", rows )
        conn.commit()
        conn.close()


            
