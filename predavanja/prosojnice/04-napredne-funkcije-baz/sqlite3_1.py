import sqlite3

# testna baza
baza = "test2.db"

with sqlite3.connect(baza) as con:
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

input("Primer: Katere tabele so v bazi?")

with sqlite3.connect(baza) as con:
    cur = con.cursor()
    res = cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    print(res.fetchall())


input("Primer: Katere vrstice so v tabeli?")            
with sqlite3.connect(baza) as con:
    cur = con.cursor()
    cur.execute("SELECT * from Cars")
    print(cur.fetchall())
    print("Še enkrat")
    print(cur.fetchall()) # ko kurzor enkrat vrne podatke se "izčrpa"

input("Primer: Poizvedba z iteracijo po 'odzivniku'.")

with sqlite3.connect(baza) as con:
    cur = con.cursor()
    cur.execute("SELECT * from Cars")
    for podatek in cur:
        print(podatek)

input("Primer interaktivne poizvedbe,  uporaba znaka '?'")
with sqlite3.connect(baza) as con:
    cur = con.cursor()
    kaj = input("Cena katerega vozila te zanima:")
    cur.execute("SELECT Price FROM Cars WHERE Name LIKE ?", (kaj,))
    print(cur.fetchone())

input("Primer interaktivne poizvedbe, uporaba ':ključ', preverjanje rezultata.")

with sqlite3.connect(baza) as con:
    cur = con.cursor()
    kaj = input("Katero vozilo te zanima:").strip()
    cur.execute("SELECT Price FROM Cars WHERE Name LIKE :cena", {"cena":kaj})
    rez = cur.fetchall()
    if len(rez) == 0:
        print("Ni takega vozila ({0}).".format(kaj))
    else:
        print("Cena vozila {0} je {1}.".format(kaj, rez[0][0]))

input("Primer: večkratno vstavljanje.")

cars = [
    (1, 'Audi2', 52643),
    (2, 'MercedesX', 57642),
    (3, 'Škoda', 9000),
    (4, 'Volvek', 29000),
    (5, 'Bentley7', 350000),
    (6, 'HummerU', 41400),
    (7, 'VolkswagenPassat', 21600)
]
print("Vstavljamo: ", cars)
with sqlite3.connect(baza) as con:
    cur = con.cursor()
    cur.executemany("INSERT INTO Cars VALUES(?, ?, ?)", cars)
    cur.execute("SELECT * from Cars")
    print("V tabeli imamo:")
    print(cur.fetchall())
    
input("Uporaba generatorja vrstic sqlite3.Row. Namesto n-terk, za vrstice vračamo objekte.")
with sqlite3.connect(baza) as con:
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("SELECT * from Cars")
    for vrstica in cur:
        print(vrstica["Name"])
    

