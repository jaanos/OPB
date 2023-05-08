from bottleext import *
import sqlite3

# KONFIGURACIJA
baza_datoteka = 'banka.db'

# Odkomentiraj, če želiš sporočila o napakah
debug(True) # za izpise pri razvoju


@get('/')
def index(cur):
    return 'Začetna stran'


############################################
### Komitent
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
    return template("komitenti_uredi.html")


@get("/komitenti/uredi/<emso>")
def komitenti_uredi(cur, emso):
    raise NotImplementedError


@get("/komitenti/brisi/<emso>")
def komitenti_brisi(cur, emso):
    raise NotImplementedError


############################################
### Kraji
############################################

@get('/kraji')
def kraji(cur):
    cur.execute("""
        SELECT posta, kraj FROM kraj
    """)
    return template('kraji.html', poste=cur)


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
        nastavi_sporocilo(f"Kraji s poštno številko {posta} ne obstaja!")
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

@get('/racuni')
def racuni(cur):
    cur.execute("""
        SELECT oseba.ime, oseba.priimek, racun.racun
        FROM racun JOIN oseba ON racun.lastnik_id = oseba.emso
    """)
    return template('racuni.html', racuni=cur)


if __name__ == "__main__":
    run()
