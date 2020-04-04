from bottle import *
import sqlite3

# KONFIGURACIJA
baza_datoteka = 'banka.db'

# Odkomentiraj, če želiš sporočila o napakah
debug(True)  # za izpise pri razvoju

napakaSporocilo = None

def nastaviSporocilo(sporocilo = None):
    global napakaSporocilo
    staro = napakaSporocilo
    napakaSporocilo = sporocilo
    return staro 
# Mapa za statične vire (slike, css, ...)
static_dir = "./static"

# streženje statičnih datotek
@route("/static/<filename:path>")
def static(filename):
    return static_file(filename, root=static_dir)

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
    napaka = nastaviSporocilo()
    cur = baza.cursor()
    poste = cur.execute("""
        SELECT postna_st, posta FROM posta
    """)
    return template('poste.html', poste=poste, napaka=napaka)

@get('/racuni')
def racuni():
    cur = baza.cursor()
    racuni = cur.execute("""
        SELECT oseba.ime, oseba.priimek, racun.racun FROM racun 
        INNER JOIN oseba ON oseba.emso = racun.lastnik_id
    """)
    return template('racuni.html', racuni=racuni)


@get('/poste/dodaj')
def dodaj_posto_get():
    return template('posta-edit.html')

@post('/poste/dodaj') 
def dodaj_posto():
    postna_st = request.forms.postna_st
    posta = request.forms.posta
    cur = baza.cursor()
    cur.execute("INSERT INTO posta (postna_st, posta) VALUES (?, ?)", (postna_st, posta))
    redirect('/poste')

@post('/poste/brisi/<postna_st>') 
def brisi_posto(postna_st):
    cur = baza.cursor()
    try:
        cur.execute("DELETE FROM posta WHERE postna_st = ?", (postna_st, ))
    except:
        nastaviSporocilo('Brisanje pošte {0} ni bilo uspešno.'.format(postna_st)) 
    redirect('/poste')

@get('/poste/uredi/<postna_st>')
def uredi_posto_get(postna_st):
    cur = baza.cursor()
    posta = cur.execute("SELECT postna_st, posta FROM posta WHERE postna_st = ?", (postna_st,)).fetchone()
    return template('posta-edit.html', posta=posta)

@post('/poste/uredi/<postna_st>')
def uredi_posto_post(postna_st):
    posta = request.forms.posta
    cur = baza.cursor()
    cur.execute("UPDATE posta SET posta = ? WHERE postna_st = ?", (posta, postna_st))
    redirect('/poste')


baza = sqlite3.connect(baza_datoteka, isolation_level=None)
baza.set_trace_callback(print) # izpis sql stavkov v terminal (za debugiranje pri razvoju)
# zapoved upoštevanja omejitev FOREIGN KEY
cur = baza.cursor()
cur.execute("PRAGMA foreign_keys = ON;")

# reloader=True nam olajša razvoj (ozveževanje sproti - razvoj)
run(host='localhost', port=8080, reloader=True)
