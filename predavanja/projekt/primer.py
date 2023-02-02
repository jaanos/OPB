#!/usr/bin/python
# -*- encoding: utf-8 -*-
 
from bottle import *
import auth
import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s sumniki

# Odkomentiraj, če želiš sporočila o napakah
debug(True)

@get('/')
def index():
    cur.execute("SELECT * FROM oseba ORDER BY priimek, ime")
    return template('komitenti.html', osebe=cur.fetchall())

@get('/transakcije/:x/')
def transakcije(x):
    cur.execute("SELECT * FROM transakcija WHERE znesek > %s ORDER BY znesek, id", [int(x)])
    return template('transakcije.html', x=x, transakcije=cur.fetchall())



######################################################################
# Glavni program

# priklopimo se na bazo
conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password)
conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT) # onemogocimo transakcije
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor) 

# poženemo strežnik na portu 8080, glej http://localhost:8080/
run(host='localhost', port=8080)
