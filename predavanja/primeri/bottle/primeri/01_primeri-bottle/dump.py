# -*- encoding: utf-8 -*-

import sqlite3, os

# Takole naredimo SQL stavke, ki jih nato lahko odnesemo na drugo bazo
# in s tem prenesemo vsebino baze.

baza_datoteka = 'urnik.db'
sql_datoteka = 'dump.sql'

baza = sqlite3.connect(baza_datoteka, isolation_level=None)

with open(sql_datoteka, 'w') as f:
    for line in baza.iterdump():
        f.write('%s\n' % line.encode("utf-8"))

# Datoteka sql_datoteka zdaj vsebuje SQL stavke, ki naredijo bazo
# in vnesejo podatke.
