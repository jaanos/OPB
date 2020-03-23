from bottle import *
import sqlite3

# KONFIGURACIJA
baza_datoteka = 'banka.db'

# Odkomentiraj, če želiš sporočila o napakah
debug(True)  # za izpise pri razvoju


@get('/')
def index():
    return 'Začetna stran'

@get('/komitenti')
def komitenti():
    cur = baza.cursor()
    komitenti = cur.execute("""
        SELECT ime, priimek, emso, ulica, hisna_stevilka, posta.postna_st, posta.posta FROM oseba
        INNER JOIN posta ON posta.postna_st = oseba.posta_id 
        ORDER BY oseba.priimek
    """)
    return template('komitenti.html', komitenti=komitenti)

@get('/poste')
def poste():
    cur = baza.cursor()
    poste = cur.execute("""
        SELECT postna_st, posta FROM posta
    """)
    return template('poste.html', poste=poste)

@get('/racuni')
def racuni():
    cur = baza.cursor()
    racuni = cur.execute("""
        SELECT oseba.ime, oseba.priimek, racun.racun FROM racun 
        INNER JOIN oseba ON oseba.emso = racun.lastnik_id
    """)
    return template('racuni.html', racuni=racuni)


@post('/poste/dodaj') # or @route('/prijava', method='POST')
def dodaj_posto():
    postna_st = request.forms.get('postna_st')
    posta = request.forms.get('posta')
    cur = baza.cursor()
    cur.execute("INSERT INTO posta (postna_st, posta) VALUES (?, ?)", (postna_st, posta))
    redirect('/poste')


baza = sqlite3.connect(baza_datoteka, isolation_level=None)
baza.set_trace_callback(print) # izpis sql stavkov v terminal (za debugiranje pri razvoju)
# zapoved upoštevanja omejitev FOREIGN KEY
cur = baza.cursor()
cur.execute("PRAGMA foreign_keys = ON;")

# reloader=True nam olajša razvoj (ozveževanje sproti - razvoj)
run(host='localhost', port=8080, reloader=True)
