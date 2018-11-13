import csv, sqlite3, sys, os


if __name__ == "__main__":
    conn = sqlite3.connect("os2.db")
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS ccl")
    conn.commit()
    cur.execute("""CREATE TABLE ccl (
        cand_id TEXT(9),
        cmte_id TEXT(9),
        cmte_type TEXT(1),
        cmte_designation TEXT(1),
        year TEXT(4));"""
        )
    conn.commit()

    with open("ccl.txt", errors="ignore") as input:
        counter = 0
        reader = csv.reader(input, delimiter="|")
        rows = [(row[0], row[3], row[4], row[5], row[2]) for row in reader]
        cur.executemany("""INSERT INTO ccl (
            cand_id,
            cmte_id,
            cmte_type,
            cmte_designation,
            year
            ) VALUES (?, ?, ?, ?, ?);""", rows )
        conn.commit()
        conn.close()


            
