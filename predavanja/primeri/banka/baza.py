import sqlite3

baza = 'banka.db'


def ustvari_bazo():
    with sqlite3.connect(baza) as conn:
        cur = conn.cursor()
        with open('banka.sql') as f:
            cur.executescript(f.read())