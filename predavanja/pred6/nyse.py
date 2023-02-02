#!/usr/bin/env python3

### Prenos baze NYSE v sqlite3

import sqlite3        # Knjižnica za delo z bazo
import csv            # Knjižnica za delo s CSV datotekami
import urllib.request # Knjižnica za delo s spletom
import re             # Knjižnica za delo z regularnimi izrazi

### Nastavitve

# Datoteka, v kateri je baza
BAZA = "nyse.db"

# URL, na katerem dobimo podatke
URL = "http://online.wsj.com/public/resources/documents/NYSE.csv"

MESECI = {'Jan':1, 'January':1,
          'Feb':2, 'February':2,
          'Mar':3, 'March' : 3,
          'Apr':4,  # dopiši
          'May':5,
          'Jun':6,
          'Jul':7,
          'Aug':8,
          'Sep':9,
          'Oct':10,
          'Nov':11,
          'Dec':12}

### Program

### 1. NAREDIMO BAZO, ČE JE ŠE NIMAMO

# Naredimo povezavo z bazo. Funkcija sqlite3.connect vrne objekt,
# ki hrani podatke o povezavi z bazo.
baza = sqlite3.connect(BAZA)

# Naredimo tabelo delnica, če je še ni
baza.execute('''CREATE TABLE IF NOT EXISTS delnica (
  symbol TEXT PRIMARY KEY,
  name TEXT
)''')

# Naredimo tabelo promet, če je še ni
baza.execute('''CREATE TABLE IF NOT EXISTS promet (
   symbol TEXT REFERENCES delnica (symbol),
   datetime TEXT,
   open REAL,
   high REAL,
   low REAL,
   close REAL
)''')

# 2. PREBEREMO PODATKE S SPLETA

spletna_stran = urllib.request.urlopen(URL)

prva_vrstica = spletna_stran.readline()
if prva_vrstica != b'NYSE Stock Exchange\n':
    print ('Spletna stran nima prave prve vrstice: {0}'.format(prva_vrstica))
    exit()

druga_vrstica = str(spletna_stran.readline())
m = re.search(r'(\w+) (\d\d), (\d\d\d\d) (\d+):(\d+) (\w\w)', druga_vrstica)
if not m:
    print ('Spletna stran nima prave druge vrstice: {0}'.format(druga_vrstica))
    exit ()
mesec = MESECI[m.group(1)]
dan = int(m.group(2))
leto = int(m.group(3))
ura = int(m.group(4)) + (12 if m.group(6) == 'PM' else 0)
minuta = int(m.group(5))
cas = '{0:04}-{1:02}-{2:02} {3:02}:{4:02}:00.000'.format(leto,mesec,dan,ura,minuta)

# Preskočimo prazno vrstico
tretja_vrstica = spletna_stran.readline()
if tretja_vrstica != b'\n':
    print ('Spletna stran nima prave tretje vrstice: {0}'.format(tretja_vrstica))
    exit ()

# Preskočimo vrstico z imeni stolpcev
cetrta_vrstica = spletna_stran.readline()
if cetrta_vrstica != b'Name,Symbol,Open,High,Low,Close,Net Chg,% Chg,Volume,52 Wk High,52 Wk Low,Div,Yield,P/E,YTD % Chg\n':
    print ('Spletna stran nima prave četrte vrstice: {0}'.format(cetrta_vrstica))
    exit ()

### 3. PODATKE SHRANIMO V BAZO

# Pomožna funkcija, ki pretvarja vrednosti delnic
def vrednost(s):
    return (None if s == '...' else float(s))

# Naredimo CSV razpredelnico
razpredelnica = csv.reader([v.decode() for v in spletna_stran])

cnt = 0
for vrstica in razpredelnica:
    print(type(vrstica))
    name = vrstica[0]
    symbol = vrstica[1]
    value_open = vrednost(vrstica[2])
    value_high = vrednost(vrstica[3])
    value_low = vrednost(vrstica[4])
    value_close = vrednost(vrstica[5])
    # Dodamo delnico, če je še ni
    c = baza.cursor()
    c.execute('SELECT 1 FROM delnica WHERE symbol=?', [symbol])
    if list(c) == []:
        print ('NOVA DELNICA: {0}, {1}'.format(symbol, name))
        baza.execute("""INSERT INTO delnica VALUES (?,?)""", (symbol,name))
    c.close()
    # Vstavimo vrstico v promet
    # POTREBNA IZBOLJSAVA: vrstice ne dodamo, če ta zapis že imamo
    print ("Vstavljam {0}".format(symbol))
    baza.execute("""INSERT INTO promet VALUES (?,?,?,?,?,?)""",
                 (symbol, cas, value_open, value_high, value_low, value_close))


# Obvezno moramo narediti commit, sicer se ne zgodi nič
baza.commit()
print("konec")
