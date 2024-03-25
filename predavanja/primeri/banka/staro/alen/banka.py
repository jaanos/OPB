from bottle import *
import sqlite3
import hashlib

# KONFIGURACIJA
baza_datoteka = 'banka.db'

# Odkomentiraj, če želiš sporočila o napakah
debug(True)  # za izpise pri razvoju

# napakaSporocilo = None

def nastaviSporocilo(sporocilo = None):
    # global napakaSporocilo
    staro = request.get_cookie("sporocilo", secret=skrivnost)
    if sporocilo is None:
        response.delete_cookie('sporocilo')
    else:
        response.set_cookie('sporocilo', sporocilo, path="/", secret=skrivnost)
    return staro 
    
# Mapa za statične vire (slike, css, ...)
static_dir = "./static"

skrivnost = "rODX3ulHw3ZYRdbIVcp1IfJTDn8iQTH6TFaNBgrSkjIulr"
# streženje statičnih datotek

def preveriUporabnika(): 
    username = request.get_cookie("username", secret=skrivnost)
    if username:
        cur = baza.cursor()    
        uporabni = None
        try: 
            uporabnik = cur.execute("SELECT * FROM oseba WHERE username = ?", (username, )).fetchone()
        except:
            uporabnik = None
        if uporabnik: 
            return uporabnik
    redirect('/prijava')

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
    uporabnik = preveriUporabnika()
    if uporabnik is None: 
        return
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
    uporabnik = preveriUporabnika()
    if uporabnik is None: 
        return
    cur = baza.cursor()
    try:
        cur.execute("DELETE FROM oseba WHERE emso = ?", (emso, ))
    except:
        nastaviSporocilo('Brisanje osebe z EMŠO {0} ni bilo uspešno.'.format(emso)) 
    redirect('/komitenti')

@get('/komitenti/dodaj')
def dodaj_komitenta_get():
    uporabnik = preveriUporabnika()
    if uporabnik is None: 
        return
    poste = cur.execute("SELECT postna_st, posta FROM posta")
    return template('komitent-edit.html', poste=poste, naslov="Dodaj komitenta")

@post('/komitenti/dodaj') 
def dodaj_komitenta_post():
    uporabnik = preveriUporabnika()
    if uporabnik is None: 
        return
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
    uporabnik = preveriUporabnika()
    if uporabnik is None: 
        return
    cur = baza.cursor()
    komitent = cur.execute("SELECT emso, ime, priimek, ulica, hisna_stevilka, posta_id FROM oseba WHERE emso = ?", (emso,)).fetchone()
    poste = cur.execute("SELECT postna_st, posta FROM posta")
    return template('komitent-edit.html', komitent=komitent, poste=poste, naslov="Uredi komitenta")

@post('/komitenti/uredi/<emso>')
def uredi_komitenta_post(emso):
    uporabnik = preveriUporabnika()
    if uporabnik is None: 
        return
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
    uporabnik = preveriUporabnika()
    if uporabnik is None: 
        return
    napaka = nastaviSporocilo()
    cur = baza.cursor()
    poste = cur.execute("""
        SELECT postna_st, posta FROM posta
    """)
    return template('poste.html', poste=poste, napaka=napaka)

@get('/poste/dodaj')
def dodaj_posto_get():
    uporabnik = preveriUporabnika()
    if uporabnik is None: 
        return
    return template('posta-edit.html')

@post('/poste/dodaj') 
def dodaj_posto():
    uporabnik = preveriUporabnika()
    if uporabnik is None: 
        return
    postna_st = request.forms.postna_st
    posta = request.forms.posta
    cur = baza.cursor()
    cur.execute("INSERT INTO posta (postna_st, posta) VALUES (?, ?)", (postna_st, posta))
    redirect('/poste')

@post('/poste/brisi/<postna_st>') 
def brisi_posto(postna_st):
    uporabnik = preveriUporabnika()
    if uporabnik is None: 
        return
    cur = baza.cursor()
    try:
        cur.execute("DELETE FROM posta WHERE postna_st = ?", (postna_st, ))
    except:
        nastaviSporocilo('Brisanje pošte {0} ni bilo uspešno.'.format(postna_st)) 
    redirect('/poste')

@get('/poste/uredi/<postna_st>')
def uredi_posto_get(postna_st):
    uporabnik = preveriUporabnika()
    if uporabnik is None: 
        return
    cur = baza.cursor()
    posta = cur.execute("SELECT postna_st, posta FROM posta WHERE postna_st = ?", (postna_st,)).fetchone()
    return template('posta-edit.html', posta=posta)

@post('/poste/uredi/<postna_st>')
def uredi_posto_post(postna_st):
    uporabnik = preveriUporabnika()
    if uporabnik is None: 
        return
    posta = request.forms.posta
    cur = baza.cursor()
    cur.execute("UPDATE posta SET posta = ? WHERE postna_st = ?", (posta, postna_st))
    redirect('/poste')


############################################
### Račun
############################################

@get('/komitenti/<emso>/racuni')
def racuni_komitenta(emso):
    uporabnik = preveriUporabnika()
    if uporabnik is None: 
        return
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
    uporabnik = preveriUporabnika()
    if uporabnik is None: 
        return
    cur = baza.cursor()
    cur.execute("INSERT INTO racun (lastnik_id) VALUES (?)", (emso, ))
    redirect('/komitenti/{0}/racuni'.format(emso))

@post('/komitenti/<emso>/racuni/<racun>/brisi')
def brisi_racun_komitenta(emso, racun):
    uporabnik = preveriUporabnika()
    if uporabnik is None: 
        return    
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
    uporabnik = preveriUporabnika()
    if uporabnik is None: 
        return    
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
    uporabnik = preveriUporabnika()
    if uporabnik is None: 
        return
    oseba = cur.execute("SELECT ime, priimek FROM oseba WHERE emso = ?", (emso, )).fetchone()
    ime = oseba[0]
    priimek = oseba[1]
    stanje = cur.execute("SELECT sum(znesek) FROM transakcija WHERE racun_id = ?", (racun, )).fetchone()
    return template('transakcija-edit.html', ime=ime, priimek=priimek, emso=emso, racun=racun, stanje=stanje[0])

@post('/komitenti/<emso>/racuni/<racun>/transakcije/dodaj')
def dodaj_transakcijo_na_racuni_komitenta_post(emso, racun):
    uporabnik = preveriUporabnika()
    if uporabnik is None: 
        return
    znesek = request.forms.znesek
    cur = baza.cursor()
    cur.execute("INSERT INTO transakcija (racun_id, znesek) VALUES (?, ?)", (racun, znesek))
    redirect('/komitenti/{0}/racuni/{1}/transakcije'.format(emso, racun))
    

############################################
### Registracija, prijava
############################################

def hashGesla(s):
    m = hashlib.sha256()
    m.update(s.encode("utf-8"))
    return m.hexdigest()

@get('/registracija')
def registracija_get():
    napaka = nastaviSporocilo()
    return template('registracija.html', napaka=napaka)

@post('/registracija')
def registracija_post():
    emso = request.forms.emso
    username = request.forms.username
    password = request.forms.password
    password2 = request.forms.password2
    if emso is None or username is None or password is None or password2 is None:
        nastaviSporocilo('Registracija ni možna') 
        redirect('/registracija')
        return
    cur = baza.cursor()    
    uporabnik = None
    try: 
        uporabnik = cur.execute("SELECT * FROM oseba WHERE emso = ?", (emso, )).fetchone()
    except:
        uporabnik = None
    if uporabnik is None:
        nastaviSporocilo('Registracija ni možna') 
        redirect('/registracija')
        return
    if len(password) < 4:
        nastaviSporocilo('Geslo mora imeti vsaj 4 znake.') 
        redirect('/registracija')
        return
    if password != password2:
        nastaviSporocilo('Gesli se ne ujemata.') 
        redirect('/registracija')
        return
    zgostitev = hashGesla(password)
    cur.execute("UPDATE oseba SET username = ?, password = ? WHERE emso = ?", (username, zgostitev, emso))
    response.set_cookie('username', username, secret=skrivnost)
    redirect('/komitenti')


@get('/prijava')
def prijava_get():
    napaka = nastaviSporocilo()
    return template('prijava.html', napaka=napaka)

@post('/prijava')
def prijava_post():
    username = request.forms.username
    password = request.forms.password
    if username is None or password is None:
        nastaviSporocilo('Uporabniško ima in geslo morata biti neprazna') 
        redirect('/prijava')
        return
    cur = baza.cursor()    
    hashBaza = None
    try: 
        hashBaza = cur.execute("SELECT password FROM oseba WHERE username = ?", (username, )).fetchone()
        hashBaza = hashBaza[0]
    except:
        hashBaza = None
    if hashBaza is None:
        nastaviSporocilo('Uporabniško geslo ali ime nista ustrezni') 
        redirect('/prijava')
        return
    if hashGesla(password) != hashBaza:
        nastaviSporocilo('Uporabniško geslo ali ime nista ustrezni') 
        redirect('/prijava')
        return
    response.set_cookie('username', username, secret=skrivnost)
    redirect('/komitenti')
    
@get('/odjava')
def odjava_get():
    response.delete_cookie('username')
    redirect('/prijava')


baza = sqlite3.connect(baza_datoteka, isolation_level=None)
baza.set_trace_callback(print) # izpis sql stavkov v terminal (za debugiranje pri razvoju)
# zapoved upoštevanja omejitev FOREIGN KEY
cur = baza.cursor()
cur.execute("PRAGMA foreign_keys = ON;")

# reloader=True nam olajša razvoj (ozveževanje sproti - razvoj)
run(host='localhost', port=8080, reloader=True)
