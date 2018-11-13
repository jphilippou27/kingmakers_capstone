import csv, sqlite3, sys


if __name__ == "__main__":
    conn = sqlite3.connect("os2.db")
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS cmte2cand")
    conn.commit()
    cur.execute("""CREATE TABLE cmte2cand (
        trans_id TEXT(32),
        filer_id TEXT(9), 
        name TEXT(200),
        alt_id TEXT(9), 
        cand_id TEXT(9), 
        amendment TEXT(1), 
        trans_type TEXT(3),
        filer_type TEXT(3),
        filer_city TEXT(30),
        filer_state TEXT(2),
        filer_zip TEXT(5),
        filer_employer TEXT(38),
        filer_occupation TEXT(38),
        date TEXT(10), 
        amount REAL, 
        memo TEXT(100));"""
        )
    conn.commit()

    with open("cmte2cand.txt", errors="ignore") as input:
        counter = 0
        reader = csv.reader(input, delimiter="|")
        rows = [(row[17], row[0], row[7], row[15], row[16], row[1], row[5], row[6], row[8], row[9], row[10], row[11], row[12], row[13][4:8] + "-" + row[13][0:2] + "-" + row[13][2:4], row[14], row[20] ) for row in reader]
    cur.executemany("""INSERT INTO cmte2cand (
        trans_id,
        filer_id, 
        name, 
        alt_id, 
        cand_id, 
        amendment,
        trans_type,
        filer_type,
        filer_city,
        filer_state,
        filer_zip,
        filer_employer,
        filer_occupation,
        date,
        amount, 
        memo
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);""", rows )
    conn.commit()
    conn.close()


            
