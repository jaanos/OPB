import sqlite3
import csv

baza_datoteka = 'banka.db'

def uvoziSQL(cur, datoteka):
    with open(datoteka) as f:
        koda = f.read()
        cur.executescript(koda)

# Uvoz preko SQL skript
# with sqlite3.connect(baza_datoteka) as baza:
#     cur = baza.cursor()
#     uvoziSQL(cur, 'banka.sql')
#     uvoziSQL(cur, 'podatki/posta.sql')
#     uvoziSQL(cur, 'podatki/oseba.sql')
#     uvoziSQL(cur, 'podatki/racun.sql')
#     uvoziSQL(cur, 'podatki/transakcija.sql')

def uvoziCSV(cur, tabela):
    with open('podatki/{0}.csv'.format(tabela)) as csvfile:
        podatki = csv.reader(csvfile)
        vsiPodatki = [vrstica for vrstica in podatki]
        glava = vsiPodatki[0]
        vrstice = vsiPodatki[1:]
        cur.executemany("INSERT INTO {0} ({1}) VALUES ({2})".format(
            tabela, ",".join(glava), ",".join(['?']*len(glava))), vrstice)

with sqlite3.connect(baza_datoteka) as baza:
    cur = baza.cursor()
    uvoziSQL(cur, 'banka.sql')
    uvoziCSV(cur, 'posta')
    uvoziCSV(cur, 'oseba')
    uvoziCSV(cur, 'racun')
    uvoziCSV(cur, 'transakcija')
