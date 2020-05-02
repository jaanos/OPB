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

############################################
### Komitent
############################################

@get('/komitenti')
def komitenti():
    napaka = nastaviSporocilo()
    cur = baza.cursor()
    komitenti = cur.execute("""
        SELECT ime, priimek, emso, ulica, hisna_stevilka, posta.postna_st, posta.posta FROM oseba
        INNER JOIN posta ON posta.postna_st = oseba.posta_id 
        ORDER BY oseba.priimek
    """)
    return template('komitenti.html', komitenti=komitenti, napaka=napaka)

@post('/komitenti/brisi/<emso>')
def brisi_komitenta(emso):
    cur = baza.cursor()
    try:
        cur.execute("DELETE FROM oseba WHERE emso = ?", (emso, ))
    except:
        nastaviSporocilo('Brisanje osebe z EMŠO {0} ni bilo uspešno.'.format(emso)) 
    redirect('/komitenti')

@get('/komitenti/dodaj')
def dodaj_komitenta_get():
    poste = cur.execute("SELECT postna_st, posta FROM posta")
    return template('komitent-edit.html', poste=poste, naslov="Dodaj komitenta")

@post('/komitenti/dodaj') 
def dodaj_komitenta_post():
    emso = request.forms.emso
    ime = request.forms.ime
    priimek = request.forms.priimek
    ulica = request.forms.ulica
    hisna_stevilka = request.forms.hisna_stevilka
    posta_id = request.forms.posta_id
    cur = baza.cursor()
    cur.execute("INSERT INTO oseba (emso, ime, priimek, ulica, hisna_stevilka, posta_id) VALUES (?, ?, ?, ?, ?, ?)", 
         (emso, ime, priimek, ulica, hisna_stevilka, posta_id))
    redirect('/komitenti')


@get('/komitenti/uredi/<emso>')
def uredi_komitenta_get(emso):
    cur = baza.cursor()
    komitent = cur.execute("SELECT emso, ime, priimek, ulica, hisna_stevilka, posta_id FROM oseba WHERE emso = ?", (emso,)).fetchone()
    poste = cur.execute("SELECT postna_st, posta FROM posta")
    return template('komitent-edit.html', komitent=komitent, poste=poste, naslov="Uredi komitenta")

@post('/komitenti/uredi/<emso>')
def uredi_komitenta_post(emso):
    novi_emso = request.forms.emso
    ime = request.forms.ime
    priimek = request.forms.priimek
    ulica = request.forms.ulica
    hisna_stevilka = request.forms.hisna_stevilka
    posta_id = request.forms.posta_id
    cur = baza.cursor()
    cur.execute("UPDATE oseba SET emso = ?, ime = ?, priimek = ?, ulica = ?, hisna_stevilka = ?, posta_id = ? WHERE emso = ?", 
         (novi_emso, ime, priimek, ulica, hisna_stevilka, posta_id, emso))
    redirect('/komitenti')


############################################
### Posta
############################################

@get('/poste')
def poste():
    napaka = nastaviSporocilo()
    cur = baza.cursor()
    poste = cur.execute("""
        SELECT postna_st, posta FROM posta
    """)
    return template('poste.html', poste=poste, napaka=napaka)

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


############################################
### Račun
############################################

@get('/komitenti/<emso>/racuni')
def racuni_komitenta(emso):
    napaka = nastaviSporocilo()
    cur = baza.cursor()
    racuni = cur.execute("""
        SELECT oseba.ime, oseba.priimek, racun.racun FROM racun 
        INNER JOIN oseba ON oseba.emso = racun.lastnik_id
        WHERE oseba.emso = ?
    """, (emso, )).fetchall()
    if len(racuni) == 0:
        nastaviSporocilo('Komitent še nima računa.') 
        redirect('/komitenti')
        return
    ime = racuni[0][0]
    priimek = racuni[0][1]
    return template('racuni.html', racuni=racuni, ime=ime, priimek=priimek, emso=emso, napaka=napaka)

@get('/komitenti/<emso>/racuni/dodaj')
def dodaj_racun_komitenta(emso):
    cur = baza.cursor()
    cur.execute("INSERT INTO racun (lastnik_id) VALUES (?)", (emso, ))
    redirect('/komitenti/{0}/racuni'.format(emso))

@post('/komitenti/<emso>/racuni/<racun>/brisi')
def brisi_racun_komitenta(emso, racun):
    try:
        cur.execute("DELETE FROM racun WHERE racun = ?", (racun, ))
    except:
        nastaviSporocilo('Brisanje računa številka {0} ni bilo uspešno.'.format(racun)) 
    redirect('/komitenti/{0}/racuni'.format(emso))


############################################
### Transakcija
############################################

@get('/komitenti/<emso>/racuni/<racun>/transakcije')
def transakcije_komitenta_na_racunu(emso, racun):
    napaka = nastaviSporocilo()
    cur = baza.cursor()
    transakcije = cur.execute("SELECT id, datum, znesek FROM transakcija WHERE racun_id = ?", (racun, )).fetchall()
    stanje = cur.execute("SELECT sum(znesek) FROM transakcija WHERE racun_id = ?", (racun, )).fetchone()
    oseba = cur.execute("SELECT ime, priimek FROM oseba WHERE emso = ?", (emso, )).fetchone()
    ime = oseba[0]
    priimek = oseba[1]
    return template('transakcije.html', transakcije=transakcije, ime=ime, priimek=priimek, racun=racun,
       stanje=stanje[0], emso=emso, napaka=napaka)

@get('/komitenti/<emso>/racuni/<racun>/transakcije/dodaj')
def dodaj_transakcijo_na_racuni_komitenta_get(emso, racun):
    oseba = cur.execute("SELECT ime, priimek FROM oseba WHERE emso = ?", (emso, )).fetchone()
    ime = oseba[0]
    priimek = oseba[1]
    stanje = cur.execute("SELECT sum(znesek) FROM transakcija WHERE racun_id = ?", (racun, )).fetchone()
    return template('transakcija-edit.html', ime=ime, priimek=priimek, emso=emso, racun=racun, stanje=stanje[0])

@post('/komitenti/<emso>/racuni/<racun>/transakcije/dodaj')
def dodaj_transakcijo_na_racuni_komitenta_post(emso, racun):
    znesek = request.forms.znesek
    cur = baza.cursor()
    cur.execute("INSERT INTO transakcija (racun_id, znesek) VALUES (?, ?)", (racun, znesek))
    redirect('/komitenti/{0}/racuni/{1}/transakcije'.format(emso, racun))
    
baza = sqlite3.connect(baza_datoteka, isolation_level=None)
baza.set_trace_callback(print) # izpis sql stavkov v terminal (za debugiranje pri razvoju)
# zapoved upoštevanja omejitev FOREIGN KEY
cur = baza.cursor()
cur.execute("PRAGMA foreign_keys = ON;")

# reloader=True nam olajša razvoj (ozveževanje sproti - razvoj)
run(host='localhost', port=8080, reloader=True)
