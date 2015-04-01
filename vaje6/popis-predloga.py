#!/usr/bin/env python3
# -*- coding: utf-8 -*-

### Prenos baze popis v sqlite3

import sqlite3        # Knjižnica za delo z bazo
import csv            # Knjižnica za delo s CSV datotekami
import re             # Knjižnica za delo z regularnimi izrazi
import sys            # Knjižnica za komunikacijo s sistemom
import urllib.request # Knjižnica za delo s spletom

### Nastavitve

# Datoteka, v kateri je baza
BAZA = "popis.sqlite3"

# URL, na katerem dobimo podatke
URL = "https://raw.githubusercontent.com/jaanos/OPB14-15/master/vaje6/popis.csv"

### Program

# NAREDIMO BAZO, ČE JE ŠE NIMAMO

# Naredimo povezavo z bazo. Funkcija sqlite3.connect vrne objekt,
# ki hrani podatke o povezavi z bazo.
baza = sqlite3.connect(BAZA)

# Naredimo tabelo kraj, če je še ni
baza.execute('''CREATE TABLE IF NOT EXISTS obcina (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT
)''')

# Naredimo tabelo podatki, če je še ni
baza.execute('''CREATE TABLE IF NOT EXISTS podatki (
   obcina INTEGER REFERENCES obcina (id),
   leto INTEGER,
   polletje INTEGER,
   spol TEXT,
   starost INTEGER,
   stevilo INTEGER,
   PRIMARY KEY (obcina, leto, polletje, spol, starost)
)''')

# Pomožna funkcija, ki vrne id občine in jo po potrebi doda v bazo
def getObcina(x):
    c = baza.cursor()
    c.execute("SELECT id FROM obcina WHERE name = ?", [x])
    r = c.fetchone()
    id = -1
    if r == None:
        c.execute("INSERT INTO obcina (name) VALUES (?)", (x,))
        id = c.lastrowid
        print("Nova občina %s, id = %s" % (x, id))
    else:
        id = r[0]
    c.close()
    
# Pomožna funkcija za normalizacijo spola
def getSpol(s):
    if type(s) == str:
        if s[0] == 'm' or s[0] == 'M':
            return "Moški"
        elif s[0] == 'ž' or s[0] == 'z' or s[0] == 'Ž' or s[0] == 'Z':
            return "Ženske"
    return None

# PREBEREMO PODATKE S SPLETA
def importData():
    print("Berem %s ..." % URL)
    www = urllib.request.urlopen(URL)

    print("Berem podatke v razpredelnico...")
    raz = csv.reader([v.decode() for v in www])

    leto = [-1]
    polletje = [-1]
    starost = [-1]
    spol = ''

    print("Pišem podatke v bazo...")
    for i, l in enumerate(raz):
        # Pripravimo indeksne vrstice za leto, polletje in starost
        if i == 0:
            for j in range(1, len(l)):
                if l[j] == " ":
                   leto.append(leto[j-1])
                   polletje.append(polletje[j-1])
                else:
                    y, h = l[j].split("H")
                    leto.append(int(y))
                    polletje.append(int(h))
        elif i == 1:
            for j in range(1, len(l)):
                starost.append(int(l[j].split(" ")[0]))
        # Če je vrstica prazna, naslednja določa spol
        elif l[0] == '':
            spol = ''
        elif spol == '':
            spol = l[0]
        else:
            # TODO
            pass

    # Obvezno moramo narediti commit, sicer se ne zgodi nič
    baza.commit()
    print("Končano.")
    
# POIZVEDUJEMO ZA PODATKI
def query(obcina=None, spol=None, minst=None, maxst=None):
    c = baza.cursor()
    # TODO
    c.close()

# DODAJAMO PODATKE V BAZO
def add(obcina, leto, polletje, spol, starost, stevilo):
    # TODO
    pass

if __name__ == '__main__':
    ok = len(sys.argv) > 1
    if ok:
        if sys.argv[1] == "import":
            importData()
        elif sys.argv[1] == "query":
            obcina=None
            spol=None
            minst=None
            maxst=None
            for i in range(2, len(sys.argv)):
                ok = True
                m = re.match(r'^(obcina|spol|starost)([=<>])(.+)$', sys.argv[i])
                if m == None:
                    ok = False
                elif m.group(1) == "obcina" and m.group(2) == "=":
                    obcina = m.group(3)
                elif m.group(1) == "spol" and m.group(2) == "=":
                    spol = m.group(3)
                elif m.group(1) == "starost":
                    if m.group(2) == ">":
                        minst = m.group(3)
                    elif m.group(2) == "<":
                        maxst = m.group(3)
                    else:
                        minst = m.group(3)
                        maxst = m.group(3)
                else:
                    ok = False
                if not ok:
                    print("Ignoriram neznan parameter: %s" % sys.argv[i])
            ok = True
            query(obcina, spol, minst, maxst)
        elif sys.argv[1] == "add" and len(sys.argv) > 7:
            try:
                obcina = sys.argv[2]
                leto = int(sys.argv[3])
                polletje = int(sys.argv[4])
                spol = getSpol(sys.argv[5])
                starost = int(sys.argv[6])
                stevilo = int(sys.argv[7])
                if polletje < 1 or polletje > 2:
                    print("Napačno polletje!")
                elif spol == None:
                    print("Napačen spol!")
                elif starost < 0 or starost > 85:
                    print("Neveljavna starost!")
                elif stevilo < 0:
                    print("Napačno število!")
                else:
                    add(obcina, leto, polletje, spol, starost, stevilo)
            except:
                ok = False
        else:
            ok = False
    if not ok:
        print("Uporaba: %s { import | query [obcina=...] [spol={M|Ž}] [starost{<|=|>}...] ... | add občina leto {1|2} {M|Ž} starost število }" % sys.argv[0])
