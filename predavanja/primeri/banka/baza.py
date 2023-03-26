import csv
import sqlite3

baza = 'banka.db'


def ustvari_bazo(conn):
    print("Ustvarjam bazo...")
    cur = conn.cursor()
    with open('banka.sql') as f:
        cur.executescript(f.read())
    cur.close()


def uvozi_csv(conn, datoteka, tabela):
    print(f"Uvažam podatke iz {datoteka} v tabelo {tabela}...")
    cur = conn.cursor()
    with open(datoteka) as f:
        rd = csv.reader(f)
        stolpci = next(rd)
        cur.executemany(f"""
            INSERT INTO {tabela} ({', '.join(stolpci)})
            VALUES ({', '.join(['?'] * len(stolpci))})
        """, rd)
    cur.close()


if __name__ == "__main__":
    with sqlite3.connect(baza) as conn:
        ustvari_bazo(conn)
        for tabela in ('kraj', 'oseba', 'racun', 'transakcija'):
            uvozi_csv(conn, f'podatki/{tabela}.csv', tabela)