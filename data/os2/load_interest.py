import csv, sqlite3, sys, os


if __name__ == "__main__":
    conn = sqlite3.connect("os2.db")
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS interest")
    conn.commit()
    cur.execute("""CREATE TABLE interest (
        code TEXT(5),
        name TEXT(100),
        industry TEXT(100),
        sector TEXT(100));"""
        )
    conn.commit()
    with open("interest.txt", errors="ignore") as input:
        counter = 0
        reader = csv.reader(input, delimiter="\t")
        rows = [(row[0], row[1], row[3], row[4] ) for row in reader]
        cur.executemany("""INSERT INTO interest (
            code,
            name,
            industry,
            sector
            ) VALUES (?, ?, ?, ?);""", rows )
        conn.commit()
        conn.close()


            
