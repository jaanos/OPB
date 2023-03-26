from bottle import *
import sqlite3

# KONFIGURACIJA
baza_datoteka = 'banka.db'

# Odkomentiraj, če želiš sporočila o napakah
debug(True) # za izpise pri razvoju


@get('/')
def index():
    return 'Začetna stran'


############################################
### Komitent
############################################

@get('/komitenti')
def komitenti():
    cur = baza.cursor()
    cur.execute("""
        SELECT ime, priimek, emso, naslov, kraj.posta, kraj.kraj
        FROM oseba JOIN kraj ON oseba.posta_id = kraj.posta
        ORDER BY oseba.priimek
    """)
    return template('komitenti.html', komitenti=cur)


############################################
### Kraji
############################################

@get('/kraji')
def kraji():
    cur = baza.cursor()
    cur.execute("""
        SELECT posta, kraj FROM kraj
    """)
    return template('kraji.html', poste=cur)


@post('/kraji/dodaj')
def kraji_dodaj_post():
    posta = request.forms.getunicode('posta')
    kraj = request.forms.getunicode('kraj')
    cur = baza.cursor()
    cur.execute("""
        INSERT INTO kraj (posta, kraj) VALUES (?, ?)
    """, (posta, kraj))
    redirect('/kraji')


############################################
### Računi
############################################

@get('/racuni')
def racuni():
    cur = baza.cursor()
    cur.execute("""
        SELECT oseba.ime, oseba.priimek, racun.racun
        FROM racun JOIN oseba ON racun.lastnik_id = oseba.emso
    """)
    return template('racuni.html', racuni=cur)


baza = sqlite3.connect(baza_datoteka)
baza.set_trace_callback(print) # izpis stavkov SQL v terminal (za razhroščevanje pri razvoju)
# zapoved upoštevanja omejitev FOREIGN KEY
cur = baza.cursor()
cur.execute("PRAGMA foreign_keys = ON;")
cur.close()

# reloader=True nam olajša razvoj (osveževanje sproti - razvoj)
run(host='localhost', port=8080, reloader=True)
