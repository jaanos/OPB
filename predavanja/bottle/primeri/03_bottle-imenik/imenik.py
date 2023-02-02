#!/usr/bin/python
# -*- encoding: utf-8 -*-

# Preprost primer uporabe bottle, v katerem hranimo telefonski imenik
# v podatkovni bazi.

from bottle import *
import sqlite3

# KONFIGURACIJA
baza_datoteka = 'imenik.db'

# Odkomentiraj, če želiš sporočila o napakah
debug(True)

@get('/')
def index():
    c = baza.cursor()
    c.execute('SELECT id, priimek, ime, stevilka FROM imenik ORDER BY priimek, ime')
    return template('imenik', imenik=c)

@post('/')
def dodaj_stevilko():
    if 'delete' in request.POST.keys():
        id = request.POST['delete'];
        baza.execute('DELETE FROM imenik WHERE id = ?', [id])
    else:
        ime = request.POST['ime']
        priimek = request.POST['priimek']
        stevilka = request.POST['stevilka']
        baza.execute('INSERT INTO imenik(ime, priimek, stevilka) VALUES (?,?,?)', [ime, priimek, stevilka])
    return index()

######################################################################
# Glavni program

# priklopimo se na bazo
baza = sqlite3.connect(baza_datoteka, isolation_level=None)
baza.text_factory = str # omogoči Unicode

# Naredimo tabelo imenik, če še ne obstaja
baza.execute("""
CREATE TABLE IF NOT EXISTS imenik (
  id   	       INTEGER PRIMARY KEY AUTOINCREMENT,
  ime          TEXT,
  priimek      TEXT,
  stevilka     TEXT
);
""")

# poženemo strežnik na portu 8080, glej http://localhost:8080/
run(host='localhost', port=8081)
