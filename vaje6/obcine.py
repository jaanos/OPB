#!/usr/bin/env python3
# -*- coding: utf-8 -*-

### Prenos baze popis v sqlite3

import sqlite3           # Knjižnica za delo z bazo
import csv               # Knjižnica za delo s CSV datotekami
import re                # Knjižnica za delo z regularnimi izrazi
import sys               # Knjižnica za komunikacijo s sistemom
import urllib.request    # Knjižnica za delo s spletom
import xml.parsers.expat # Knjižnica za branje dokumentov XML

### Nastavitve

# Datoteka, v kateri je baza
BAZA = "popis.sqlite3"

# URL, na katerem dobimo podatke
URL = "http://sl.wikipedia.org/wiki/Seznam_ob%C4%8Din_v_Sloveniji"

### Program

# NAREDIMO BAZO, ČE JE ŠE NIMAMO

# Naredimo povezavo z bazo. Funkcija sqlite3.connect vrne objekt,
# ki hrani podatke o povezavi z bazo.
baza = sqlite3.connect(BAZA)

# Naredimo tabelo kraj, če je še ni
baza.execute('''CREATE TABLE IF NOT EXISTS obcina (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ime TEXT,
  povrsina REAL,
  prebivalstvo INTEGER,
  gostota REAL,
  naselja INTEGER,
  ustanovitev INTEGER,
  pokrajina TEXT,
  regija TEXT,
  odcepitev TEXT
)''')

# Pomožna funkcija, ki vrne id občine, če ta obstaja
def getObcina(x):
    c = baza.cursor()
    c.execute("SELECT id FROM obcina WHERE ime = ?", [x])
    r = c.fetchone()
    id = None
    if r != None:
        id = r[0]
    c.close()
    return id
    
# Objekt za branje spletnih strani
class HTMLParser:
    Parser = None
    file = None
    active = False
    row = None
    data = None
    
    # Inicializacija
    def __init__(self, file):
        self.Parser = xml.parsers.expat.ParserCreate()
        self.Parser.StartElementHandler = self.handleStartElement
        self.Parser.EndElementHandler = self.handleEndElement
        self.Parser.CharacterDataHandler = self.handleCharacterData
        self.file = file
    
    # Branje
    def parse(self):
        self.Parser.ParseFile(self.file)
        baza.commit()
    
    # Začetni elementi
    def handleStartElement(self, name, attrs):
        # Tabela s podatki: začnemo z branjem
        if name == 'table' and attrs["class"] == "wikitable sortable":
            self.active = True
        elif self.active:
            # Vrstica: pripravimo vrstico
            if name == 'tr':
                self.row = [None]
            # Celica: pripravimo vsebino
            elif name == 'td':
                self.data = ""
                
    # Končni elementi
    def handleEndElement(self, name):
        # Tabela: končamo z branjem
        if name == 'table':
            self.active = False
        elif self.active:
            # Vrstica: zapišemo prebrane podatke v bazo
            if name == 'tr':
                if len(self.row) > 1:
                    self.row[2] = float(re.sub(r',', '.', self.row[2]))
                    self.row[3] = int(re.sub(r'\.', '', self.row[3]))
                    # TODO: počisti še ostale vrednosti
                    self.row[0] = getObcina(self.row[1])
                    baza.execute('''
                        REPLACE INTO obcina VALUES (?,?,?,?,?,?,?,?,?,?)
                    ''', self.row)
                self.row = None
            # Celica: dodamo v vrstico
            elif name == 'td':
                self.row.append(self.data)
                self.data = None
                
    # Branje podatkov iz celic
    def handleCharacterData(self, data):
        if self.data != None:
            self.data += data

# PREBEREMO PODATKE S SPLETA
def importData():
    print("Berem %s ..." % URL)
    www = urllib.request.urlopen(URL)
    HTMLParser(www).parse()

if __name__ == '__main__':
    ok = len(sys.argv) > 1
    if ok:
        if sys.argv[1] == "import":
            importData()
        # TODO: dodaj funkcionalnost
    else:
            ok = False
    if not ok:
        print("Uporaba: %s import" % sys.argv[0])
