from bottleext import *
from datetime import datetime
import sqlite3

# KONFIGURACIJA
baza_datoteka = 'banka.db'

# Odkomentiraj, če želiš sporočila o napakah
debug(True) # za izpise pri razvoju


@get('/')
def index(cur):
    return template('index.html')


############################################
### Komitenti
############################################

@get('/komitenti')
def komitenti(cur):
    cur.execute("""
        SELECT ime, priimek, emso, naslov, kraj.posta, kraj.kraj
        FROM oseba JOIN kraj ON oseba.posta_id = kraj.posta
        ORDER BY oseba.priimek
    """)
    return template('komitenti.html', komitenti=cur)


@get("/komitenti/dodaj")
def komitenti_dodaj(cur):
    return template("komitenti_uredi.html", poste=seznam_krajev(cur))


@post("/komitenti/dodaj")
def komitenti_dodaj_post(cur):
    emso = request.forms.getunicode('emso')
    ime = request.forms.getunicode('ime')
    priimek = request.forms.getunicode('priimek')
    naslov = request.forms.getunicode('naslov')
    posta_id = request.forms.getunicode('posta_id')
    try:
        with baza:
            cur.execute("""
                INSERT INTO oseba (emso, ime, priimek, naslov, posta_id)
                VALUES (?, ?, ?, ?, ?)
            """, (emso, ime, priimek, naslov, posta_id))
    except:
        nastavi_sporocilo(f"Dodajanje komitenta z EMŠOm {emso} ni uspelo.")
    redirect(url('komitenti'))


@get("/komitenti/uredi/<emso>")
def komitenti_uredi(cur, emso):
    cur.execute("""
        SELECT ime, priimek, naslov, posta_id FROM oseba WHERE emso = ?
    """, (emso, ))
    res = cur.fetchone()
    if res is None:
        nastavi_sporocilo(f"Komitent z EMŠOm {emso} ne obstaja!")
        redirect(url('komitenti'))
    ime, priimek, naslov, posta_id = res
    return template("komitenti_uredi.html", emso=emso, ime=ime, priimek=priimek,
                    naslov=naslov, posta_id=posta_id, poste=seznam_krajev(cur))


@post("/komitenti/uredi/<emso>")
def komitenti_uredi_post(cur, emso):
    novi_emso = request.forms.getunicode('emso')
    ime = request.forms.getunicode('ime')
    priimek = request.forms.getunicode('priimek')
    naslov = request.forms.getunicode('naslov')
    posta_id = request.forms.getunicode('posta_id')
    try:
        with baza:
            cur.execute("""
                UPDATE oseba SET emso = ?, ime = ?, priimek = ?,
                naslov = ?, posta_id = ? WHERE emso = ?
            """, (novi_emso, ime, priimek, naslov, posta_id, emso))
    except:
        nastavi_sporocilo(f"Urejanje komitenta z EMŠOm {emso} ni uspelo.")
        redirect(url('komitenti_uredi', emso=emso))
    redirect(url('komitenti'))


@post("/komitenti/brisi/<emso>")
def komitenti_brisi(cur, emso):
    try:
        with baza:
            cur.execute("""
                DELETE FROM oseba WHERE emso = ?
            """, (emso, ))
    except:
        nastavi_sporocilo(f"Brisanje osebe z EMŠOm {emso} ni uspelo.")
    redirect(url('komitenti'))


############################################
### Kraji
############################################

def seznam_krajev(cur):
    cur.execute("""
        SELECT posta, kraj FROM kraj
    """)
    return cur


@get('/kraji')
def kraji(cur):
    return template('kraji.html', poste=seznam_krajev(cur))


@get("/kraji/dodaj")
def kraji_dodaj(cur):
    return template("kraji_uredi.html")


@post('/kraji/dodaj')
def kraji_dodaj_post(cur):
    posta = request.forms.getunicode('posta')
    kraj = request.forms.getunicode('kraj')
    try:
        with baza:
            cur.execute("""
                INSERT INTO kraj (posta, kraj) VALUES (?, ?)
            """, (posta, kraj))
    except:
        nastavi_sporocilo(f"Dodajanje kraja s poštno številko {posta} ni uspelo.")
    redirect(url('kraji'))


@get("/kraji/uredi/<posta:int>")
def kraji_uredi(cur, posta):
    cur.execute("""
        SELECT kraj FROM kraj WHERE posta = ?
    """, (posta, ))
    res = cur.fetchone()
    if res is None:
        nastavi_sporocilo(f"Kraj s poštno številko {posta} ne obstaja!")
        redirect(url('kraji'))
    kraj, = res
    return template("kraji_uredi.html", posta=posta, kraj=kraj)


@post("/kraji/uredi/<posta:int>")
def kraji_uredi_post(cur, posta):
    kraj = request.forms.getunicode('kraj')
    try:
        with baza:
            cur.execute("""
                UPDATE kraj SET kraj = ? WHERE posta = ?
            """, (kraj, posta))
    except:
        nastavi_sporocilo(f"Urejanje kraja s poštno številko {posta} ni uspelo.")
        redirect(url('kraji_uredi', posta=posta))
    redirect(url('kraji'))


@post("/kraji/brisi/<posta:int>")
def kraji_brisi(cur, posta):
    try:
        with baza:
            cur.execute("""
                DELETE FROM kraj WHERE posta = ?
            """, (posta, ))
    except:
        nastavi_sporocilo(f"Brisanje kraja s poštno številko {posta} ni uspelo.")
    redirect(url('kraji'))


############################################
### Računi
############################################

def podatki_racuna(cur, racun):
    cur.execute("""
        SELECT emso, ime, priimek, COALESCE(SUM(znesek), 0) AS stanje
        FROM oseba JOIN racun ON lastnik_id = emso
        LEFT JOIN transakcija ON racun_id = racun
        WHERE racun = ?
    """, (racun, ))
    return cur.fetchone()


@get('/racuni/<emso>')
def racuni(cur, emso):
    cur.execute("""
        SELECT ime, priimek FROM oseba
        WHERE emso = ?
    """, (emso, ))
    res = cur.fetchone()
    if res is None:
        nastavi_sporocilo(f"Oseba z EMŠOm {emso} ne obstaja.")
        redirect(url('komitenti'))
    ime, priimek = res
    cur.execute("""
        SELECT racun, COALESCE(SUM(znesek), 0) AS stanje
        FROM racun LEFT JOIN transakcija
        ON racun_id = racun
        WHERE lastnik_id = ?
        GROUP BY racun
    """, (emso, ))
    return template('racuni.html', ime=ime, priimek=priimek, emso=emso, racuni=cur)


@post('/racuni/<emso>/dodaj')
def racuni_dodaj(cur, emso):
    try:
        with baza:
            cur.execute("""
                INSERT INTO racun (lastnik_id) VALUES (?)
            """, (emso, ))
    except:
        nastavi_sporocilo(f"Dodajanje računa za osebo z EMŠOm {emso} ni uspelo.")
    redirect(url('racuni', emso=emso))


@post('/racuni/<emso>/brisi/<racun:int>')
def racuni_brisi(cur, emso, racun):
    try:
        with baza:
            cur.execute("""
                DELETE FROM racun WHERE racun = ? AND lastnik_id = ?
            """, (racun, emso))
    except:
        nastavi_sporocilo(f"Brisanje računa s številko {racun} ni uspelo.")
    redirect(url('racuni', emso=emso))


############################################
### Transakcije
############################################

@get('/transakcije/<racun:int>')
def transakcije(cur, racun):
    res = podatki_racuna(cur, racun)
    if res is None:
        nastavi_sporocilo(f"Račun s številko {racun} ne obstaja.")
        redirect(url('komitenti'))
    emso, ime, priimek, stanje = res
    cur.execute("""
        SELECT id, znesek, datum FROM transakcija
        WHERE racun_id = ?
        ORDER BY datum
    """, (racun, ))
    return template('transakcije.html', ime=ime, priimek=priimek, emso=emso,
                    stanje=stanje, racun=racun, transakcije=cur)


@get("/transakcije/<racun:int>/dodaj")
def transakcije_dodaj(cur, racun):
    res = podatki_racuna(cur, racun)
    if res is None:
        nastavi_sporocilo(f"Račun s številko {racun} ne obstaja.")
        redirect(url('komitenti'))
    emso, ime, priimek, stanje = res
    return template("transakcije_uredi.html", racun=racun, stanje=stanje,
                    ime=ime, priimek=priimek, 
                    datum=datetime.now().strftime("%Y-%m-%d"))


@post('/transakcije/<racun:int>/dodaj')
def transakcije_dodaj_post(cur, racun):
    znesek = request.forms.getunicode('znesek')
    datum = request.forms.getunicode('datum')
    try:
        with baza:
            cur.execute("""
                INSERT INTO transakcija (racun_id, znesek, datum) VALUES (?, ?, ?)
            """, (racun, znesek, datum))
    except:
        nastavi_sporocilo(f"Dodajanje transakcija na računu {racun} ni uspelo.")
    redirect(url('transakcije', racun=racun))


@get("/transakcije/<racun:int>/uredi/<id:int>")
def transakcije_uredi(cur, racun, id):
    res = podatki_racuna(cur, racun)
    if res is None:
        nastavi_sporocilo(f"Račun s številko {racun} ne obstaja.")
        redirect(url('komitenti'))
    emso, ime, priimek, stanje = res
    cur.execute("""
        SELECT znesek, datum FROM transakcija WHERE id = ? AND racun_id = ?
    """, (id, racun))
    res = cur.fetchone()
    if res is None:
        nastavi_sporocilo(f"Transakcija z ID-jem {id} na računu {racun} ne obstaja!")
        redirect(url('transakcije', racun=racun))
    znesek, datum = res
    return template("transakcije_uredi.html", id=id, racun=racun, stanje=stanje,
                    ime=ime, priimek=priimek, znesek=znesek, datum=datum)


@post("/transakcije/<racun:int>/uredi/<id:int>")
def transakcije_uredi_post(cur, racun, id):
    znesek = request.forms.getunicode('znesek')
    datum = request.forms.getunicode('datum')
    try:
        with baza:
            cur.execute("""
                UPDATE transakcija SET znesek = ?, datum = ?
                WHERE id = ? AND racun_id = ?
            """, (znesek, datum, id, racun))
    except:
        nastavi_sporocilo(f"Urejanje transakcije z ID-jem {id} na računu {racun} ni uspelo.")
        redirect(url('transakcije_uredi', racun=racun, id=id))
    redirect(url('transakcije', racun=racun))


@post("/transakcije/<racun:int>/brisi/<id:int>")
def transakcije_brisi(cur, racun, id):
    try:
        with baza:
            cur.execute("""
                DELETE FROM transakcija WHERE id = ? AND racun_id = ?
            """, (id, racun))
    except:
        nastavi_sporocilo(f"Brisanje transakcije z ID-jem {id} na računu {racun} ni uspelo.")
    redirect(url('transakcije', racun=racun))


if __name__ == "__main__":
    run()
