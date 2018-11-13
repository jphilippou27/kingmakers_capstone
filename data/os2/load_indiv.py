import csv, sqlite3, sys, os


if __name__ == "__main__":
    filenames = os.listdir("by_date")

    conn = sqlite3.connect("os2.db")
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS indiv")
    conn.commit()
    cur.execute("""CREATE TABLE indiv (
        trans_id TEXT(32),
        donor_id TEXT(9),
        donor_name TEXT(200),
        recip_id TEXT(9), 
        amendment TEXT(1), 
        trans_type TEXT(3),
        donor_type TEXT(3),
        donor_city TEXT(30),
        donor_state TEXT(2),
        donor_zip TEXT(5),
        donor_employer TEXT(38),
        donor_occupation TEXT(38),
        date TEXT(10), 
        amount REAL, 
        memo TEXT(100));"""
        )
    conn.commit()

    for name in filenames:
        print("opening", name)
        with open(os.path.join("by_date", name), errors="ignore") as input:
            counter = 0
            reader = csv.reader(input, delimiter="|")
            rows = [(row[16], row[15], row[7], row[0], row[1], row[5], row[6], row[8], row[9], row[10], row[11], row[12], row[13][4:8] + "-" + row[13][0:2] + "-" + row[13][2:4], row[14], row[19] ) for row in reader]
        cur.executemany("""INSERT INTO indiv (
            trans_id,
            donor_id,
            donor_name,
            recip_id, 
            amendment, 
            trans_type,
            donor_type,
            donor_city,
            donor_state,
            donor_zip,
            donor_employer,
            donor_occupation,
            date, 
            amount, 
            memo
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);""", rows )
        conn.commit()
    conn.close()


            
