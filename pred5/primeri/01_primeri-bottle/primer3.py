#!/usr/bin/python
# -*- encoding: utf-8 -*-

# Preprost primer uporabe bottle, v katerem hranimo urnik v podatkovni bazi.
# Na naslovu /ucitelji/ se mora pojaviti spisek učiteljev (v HTML, ne kot besedilo).
 
from bottle import *
import sqlite3

# KONFIGURACIJA
baza_datoteka = 'urnik.db'

# Odkomentiraj, če želiš sporočila o napakah
debug(True)

@get('/')
def index():
    return 'Pojdi raje na <a href="/ucitelji/">ta naslov</a>.'

@get('/ucitelji_slabi/')
def ucitelji_slabi():
    c = baza.cursor()
    c.execute("SELECT id,ime FROM ucitelj ORDER BY ime")
    # TAKO SE NE DELA!
    odgovor = ""
    for (uid, ime) in c:
        odgovor = odgovor + "<li>Učitelj {0} ima id {1}.</li>".format(ime, uid)
    return """<html>
              <head><title>Učitelji</title>
              <META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=utf-8">
              </head>
              <body>
                <h1>Spisek vseh učiteljev (slaba varianta)</h1>
                <ul>
                  {0}
                </ul>                
              </body>
              </html>""".format(odgovor)


@get('/ucitelji/')
def ucitelji():
    c = baza.cursor()
    c.execute("SELECT id,ime,povezava FROM ucitelj ORDER BY ime")
    # TAKO SE DELA!
    return template('ucitelji.html', ucitelji=c)



######################################################################
# Glavni program

# priklopimo se na bazo
baza = sqlite3.connect(baza_datoteka, isolation_level=None)

# poženemo strežnik na portu 8080, glej http://localhost:8080/
run(host='localhost', port=8080)
