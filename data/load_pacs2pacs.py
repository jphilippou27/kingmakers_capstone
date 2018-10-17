import csv, sqlite3, sys


if __name__ == "__main__":
    filename = ""
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        sys.exit(1)

    conn = sqlite3.connect("os.db")
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS pacs2pacs")
    conn.commit()
    cur.execute("""CREATE TABLE pacs2pacs (
        cycle TEXT(4), 
        fec_rec_id TEXT(19), 
        filer_id TEXT(9), 
        donor_cmte TEXT(50), 
        name TEXT(50), 
        city TEXT(30),
        state TEXT(2),
        zip TEXT(5),
        occupation TEXT(38),
        donor_industry TEXT(5),
        date TEXT(12),
        amount REAL, 
        recipient_id TEXT(9), 
        party TEXT(1),
        cmte_id TEXT(9),
        recip_code TEXT(2),
        recip_industry TEXT(5), 
        ammended TEXT(1), 
        report_type TEXT(3), 
        pg TEXT(1),
        microfilm TEXT(11),
        trans_type TEXT(3),
        donor_industry2 TEXT(5),
        source TEXT(5));"""
        )
    conn.commit()

    with open(filename + ".txt", errors="ignore") as input:
        counter = 0
        reader = csv.reader(input, delimiter=",", quotechar="|")
        rows = [(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18], row[19], row[20], row[21], row[22], row[23] ) for row in reader]
    cur.executemany("""INSERT INTO pacs2pacs (
        cycle, 
        fec_rec_id, 
        filer_id, 
        donor_cmte, 
        name, 
        city,
        state,
        zip,
        occupation,
        donor_industry,
        date,
        amount, 
        recipient_id, 
        party,
        cmte_id,
        recip_code,
        recip_industry, 
        ammended, 
        report_type, 
        pg,
        microfilm,
        trans_type,
        donor_industry2,
        source
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);""", rows )
    conn.commit()
    conn.close()


            
