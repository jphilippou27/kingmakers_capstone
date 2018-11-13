import csv, sqlite3, sys


if __name__ == "__main__":
    conn = sqlite3.connect("os2.db")
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS cmte_advanced;")
    conn.commit()
    cur.execute("""CREATE TABLE cmte_advanced (
        id TEXT(9), 
        name TEXT(50), 
        parent TEXT(50), 
        cand_id TEXT(9), 
        type TEXT(2), 
        party TEXT(1), 
        interest TEXT(5),
        sensitive TEXT(1)
        );"""
        )
    conn.commit()

    with open("cmte_advanced.txt", errors="ignore") as input:
        counter = 0
        reader = csv.reader(input, delimiter=",", quotechar="|")
        rows = [(row[1], row[2], row[4], row[7], row[6], row[8], row[9], row[11]) for row in reader]
    cur.executemany("""INSERT INTO cmte_advanced (
        id,
        name,
        parent,
        cand_id,
        type,
        party,
        interest,
        sensitive
        ) VALUES (?, ?, ?, ?, ?, ?, ? ,?);""", rows )
    conn.commit()
    conn.close()


            
