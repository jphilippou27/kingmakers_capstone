import csv, sqlite3, sys, os


if __name__ == "__main__":
    conn = sqlite3.connect("os2.db")
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS cmte")
    conn.commit()
    cur.execute("""CREATE TABLE cmte (
        id TEXT(9),
        name TEXT(200),
        type TEXT(1),
        designation TEXT(1),
        party TEXT(3),
        city TEXT(30),
        state TEXT(2),
        zip TEXT(5),
        interest_type TEXT(1),
        parent TEXT(200),
        cand_id TEXT(9));"""
        )
    conn.commit()

    with open("committees.txt", errors="ignore") as input:
        counter = 0
        reader = csv.reader(input, delimiter="|")
        rows = [(row[0], row[1], row[9], row[8], row[10], row[5], row[6], row[7], row[12], row[13], row[14] ) for row in reader]
        cur.executemany("""INSERT INTO cmte (
            id,
            name,
            type,
            designation,
            party,
            city,
            state,
            zip,
            interest_type,
            parent,
            cand_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);""", rows )
        conn.commit()
        conn.close()


            
