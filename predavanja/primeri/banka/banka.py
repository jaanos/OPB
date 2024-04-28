from bottleext import get, post, view, run, request, response, template, \
    redirect, static_file, url, debug, BaseTemplate
from model import Kraj, Oseba, Racun, Transakcija, vzpostavi_povezavo
import json
import os


# privzete nastavitve
SERVER_PORT = os.environ.get('BOTTLE_PORT', 8080)
RELOADER = os.environ.get('BOTTLE_RELOADER', True)
DB_PORT = os.environ.get('POSTGRES_PORT', 5432)
SKRIVNOST = 'nekaj, kar bo zelo težko uganiti!!!!  fflidnfdsnunsdi'


# Odkomentiraj, če želiš sporočila o napakah
debug(True) # za izpise pri razvoju


def izbrisi_piskotek(piskotek):
    response.delete_cookie(piskotek, path='/')


def nastavi_sporocilo(sporocilo, piskotek='sporocilo'):
    """
    Nastavi piškotek s sporočilom.
    """
    response.set_cookie(piskotek, sporocilo, secret=SKRIVNOST, path='/')


def preberi_sporocilo(piskotek='sporocilo', izbrisi=True):
    """
    Preberi sporočilo in pobriši pripadajoči piškotek.
    """
    sporocilo = request.get_cookie(piskotek, secret=SKRIVNOST)
    if izbrisi:
        izbrisi_piskotek(piskotek)
    return sporocilo


def nastavi_obrazec(piskotek, obrazec):
    """
    Zapiši vrednosti obrazca v obliki slovarja v piškotek kot niz JSON.
    """
    nastavi_sporocilo(json.dumps(obrazec), piskotek)


def preberi_obrazec(piskotek, privzeto={}, izbrisi=True):
    """
    Preberi vrednosti obrazca in pobriši pripadajoči piškotek.
    """
    try:
        return json.loads(preberi_sporocilo(piskotek, izbrisi))
    except (TypeError, json.JSONDecodeError):
        return privzeto


@get('/static/<filename:path>')
def static(filename):
    return static_file(filename, root='static')


@get('/')
def index():
    return 'Začetna stran'


############################################
### Komitenti
############################################

@get('/komitenti/')
@view('komitenti.html')
def komitenti():
    return dict(komitenti=Oseba.seznam())


@get('/komitenti/uredi/<emso>/')
@view('komitenti_uredi.html')
def komitenti_uredi(emso):
    return dict(oseba=Oseba.z_id(emso))


@post('/komitenti/uredi/<emso>/')
def komitenti_uredi_post(emso):
    nov_emso = request.forms.getunicode('emso')
    ime = request.forms.getunicode('ime')
    priimek = request.forms.getunicode('priimek')
    naslov = request.forms.getunicode('naslov')
    kraj_id = request.forms.getunicode('kraj_id')
    oseba = Oseba(ime, priimek, emso, naslov, kraj_id)
    oseba.emso = nov_emso
    try:
        oseba.shrani()
    except (TypeError, ValueError):
        # TODO - opozorilo o napaki
        # TODO - zabeleži vsebino obrazca
        redirect(url('komitenti_uredi', emso=emso))
    redirect(url('komitenti'))


@post('/komitenti/izbrisi/<emso>/')
def komitenti_izbrisi_post(emso):
    try:
        Oseba.izbrisi_id(emso)
    except (TypeError, ValueError):
        pass # TODO - izpiši sporočilo o napaki!
    redirect(url('komitenti'))


############################################
### Kraji
############################################

@get('/kraji/')
@view('kraji.html')
def kraji():
    return dict(kraji=Kraj.seznam())


@post('/kraji/dodaj/')
def kraji_dodaj_post():
    posta = request.forms.getunicode('posta')
    ime_kraja = request.forms.getunicode('kraj')
    kraj = Kraj.ustvari(posta, ime_kraja)
    try:
        kraj.shrani()
    except (TypeError, ValueError):
        nastavi_sporocilo("Dodajanje kraja ni uspelo!")
        nastavi_obrazec('kraji', kraj.vrednosti())
    redirect(url('kraji'))


@get('/kraji/uredi/<posta:int>/')
@view('kraji_uredi.html')
def kraji_uredi(posta):
    return dict(kraj=Kraj.z_id(posta))


@post('/kraji/uredi/<posta:int>/')
def kraji_uredi_post(posta):
    nova_posta = request.forms.getunicode('posta')
    ime = request.forms.getunicode('kraj')
    kraj = Kraj(posta, ime)
    kraj.posta = nova_posta
    try:
        kraj.shrani()
    except (TypeError, ValueError):
        nastavi_sporocilo(f"Urejanje kraja s pošto {posta} ni uspelo!")
        nastavi_obrazec(f'kraji_uredi{posta}', kraj.vrednosti())
        redirect(url('kraji_uredi', posta=posta))
    redirect(url('kraji'))


@post('/kraji/izbrisi/<posta:int>/')
def kraji_izbrisi_post(posta):
    try:
        Kraj.izbrisi_id(posta)
    except (TypeError, ValueError):
        pass # TODO - izpiši sporočilo o napaki!
    redirect(url('kraji'))


############################################
### Računi
############################################

@get('/racuni/')
@view('racuni.html')
def racuni():
    return dict(racuni=Racun.seznam())


@get('/racuni/<emso>/')
@view('racuni_osebe.html')
def racuni_osebe(emso):
    return dict(oseba=Oseba.z_id(emso))


############################################
### Transakcije
############################################

@get('/transakcije/')
@view('transakcije.html')
def transakcije():
    return dict(transakcije=Transakcija.seznam())


@get('/transakcije/<stevilka>/')
@view('transakcije_na_racunu.html')
def transakcije_na_racunu(stevilka):
    return dict(racun=Racun.z_id(stevilka))


BaseTemplate.defaults.update(
    Kraj=Kraj,
    Oseba=Oseba,
    Racun=Racun,
    Transakcija=Transakcija,
    preberi_sporocilo=preberi_sporocilo,
    preberi_obrazec=preberi_obrazec
)

with vzpostavi_povezavo():
    # reloader=True nam olajša razvoj (osveževanje sproti - razvoj)
    run(host='localhost', port=SERVER_PORT, reloader=RELOADER)
