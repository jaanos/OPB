## Namescanje paketa psycopg2
# Namestitev izvedemo iz ukazne vrstice.
# Ce nimamo administrativnih pravic na racunalniku
#
# python -m pip install --user psycopg2
#
# Ce jih imamo:
#
# python -m pip install psycopg2
#

# POZOR: za uporabo tega programa moramo imeti dostop podatkovne baze Postgres 
# s pravico ustvarjanja tabel.
# Bazo postgres si lahko namestimo na svojem racunalniku in v datoteki 
# `conf_baza` nastavimo ustrezne dostope.

import psycopg2

# Spremljajoca datoteka conf_baza.py s podatki za dostop
from conf_baza import *

conn_string = "host='{0}' dbname='{1}' user='{2}' password='{3}'".format(
    host, dbname, user, password)

with psycopg2.connect(conn_string) as con:
    cur = con.cursor()   # "odzivnik" za pregledovanje poizvedbe
    cur.execute("DROP TABLE IF EXISTS Cars")
    cur.execute("CREATE TABLE Cars(Id INT, Name TEXT, Price INT)")
    cur.execute("INSERT INTO Cars VALUES(1,'Audi',52642)")
    cur.execute("INSERT INTO Cars VALUES(2,'Mercedes',57127)")
    cur.execute("INSERT INTO Cars VALUES(3,'Skoda',9000)")
    cur.execute("INSERT INTO Cars VALUES(4,'Volvo',29000)")
    cur.execute("INSERT INTO Cars VALUES(5,'Bentley',350000)")
    cur.execute("INSERT INTO Cars VALUES(6,'Citroen',21000)")
    cur.execute("INSERT INTO Cars VALUES(7,'Hummer',41400)")
    cur.execute("INSERT INTO Cars VALUES(8,'Volkswagen',21600)")
    #con.commit()

# Poizvedba za vse podatke v tabeli            
with psycopg2.connect(conn_string) as con:
    cur = con.cursor()
    cur.execute("SELECT * from Cars")
    print(cur.fetchall())
    print("Še enkrat")
    print(cur.fetchall()) # ko kurzor enkrat vrne podatke se "izčrpa"

# Poizvedba z iteracijo po "odzivniku"
with psycopg2.connect(baza) as con:
   cur = con.cursor()
   cur.execute("SELECT * from Cars")
   for podatek in cur:
       print(podatek)

# Primer "interaktivne" poizvedbe - uporaba '?'
with psycopg2.connect(conn_string) as con:
   cur = con.cursor()
   kaj = input("Katero vozilo te zanima:")
   cur.execute("SELECT Price FROM Cars WHERE Name LIKE %s", (kaj,))
   print(cur.fetchone())
####
# Primer "interaktivne" poizvedbe, uporaba ':ključ', preverjanje rezultata    
with psycopg2.connect(conn_string) as con:
   cur = con.cursor()
   kaj = input("Katero vozilo te zanima:").strip()
   cur.execute("SELECT Price FROM Cars WHERE Name LIKE %(cena)s", {"cena":kaj})
   rez = cur.fetchall()
   if len(rez) == 0:
       print("Ni takega vozila ({0}).".format(kaj))
   else:
       print("Cena vozila {0} je {1}.".format(kaj, rez[0][0]))

# Večkratno vstavljanje
cars = [
    (1, 'Audi2', 52643),
    (2, 'MercedesX', 57642),
    (3, 'Škoda', 9000),
    (4, 'Volvek', 29000),
    (5, 'Bentley7', 350000),
    (6, 'HummerU', 41400),
    (7, 'VolkswagenPassat', 21600)
]

with psycopg2.connect(conn_string) as con:
    cur = con.cursor()
    cur.executemany("INSERT INTO Cars VALUES(%s, %s, %s)", cars)
    #con.commit()
    
    

