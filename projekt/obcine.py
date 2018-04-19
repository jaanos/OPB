# uvozimo ustrezne podatke za povezavo
import auth
auth.db = "sem2018_%s" % auth.user

# uvozimo psycopg2
import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki

import csv

def ustvari_tabelo():
    cur.execute("""
        CREATE TABLE obcina (
            id SERIAL PRIMARY KEY,
            ime TEXT NOT NULL,
            povrsina NUMERIC NOT NULL,
            prebivalstvo INTEGER NOT NULL,
            gostota NUMERIC NOT NULL,
            naselja INTEGER NOT NULL,
            ustanovitev INTEGER,
            pokrajina TEXT NOT NULL,
            stat_regija TEXT NOT NULL,
            odcepitev TEXT
        );
    """)
    conn.commit()

def pobrisi_tabelo():
    cur.execute("""
        DROP TABLE obcina;
    """)
    conn.commit()

def uvozi_podatke():
    with open("obcine.csv") as f:
        rd = csv.reader(f)
        next(rd) # izpusti naslovno vrstico
        for r in rd:
            r = [None if x in ('', '-') else x for x in r]
            cur.execute("""
                INSERT INTO obcina
                (ime, povrsina, prebivalstvo, gostota, naselja,
                 ustanovitev, pokrajina, stat_regija, odcepitev)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, r)
            rid, = cur.fetchone()
            print("Uvožena občina %s z ID-jem %d" % (r[0], rid))
    conn.commit()

def prebivalci(stevilo):
    cur.execute("""
        SELECT * FROM obcina
        WHERE prebivalstvo >= %s
    """, [stevilo])
    return cur.fetchall()

conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password)
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor) 
