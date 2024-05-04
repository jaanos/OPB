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
    nastavi_sporocilo(json.dumps(obrazec, default=str), piskotek)


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


@get('/komitenti/dodaj/')
@view('komitenti_dodaj.html')
def komitenti_dodaj():
    pass


@post('/komitenti/dodaj/')
def komitenti_dodaj_post():
    emso = request.forms.getunicode('emso')
    ime = request.forms.getunicode('ime')
    priimek = request.forms.getunicode('priimek')
    naslov = request.forms.getunicode('naslov')
    kraj_id = request.forms.getunicode('kraj_id')
    oseba = Oseba.ustvari(ime, priimek, emso, naslov, kraj_id)
    try:
        oseba.shrani()
    except (TypeError, ValueError):
        nastavi_sporocilo("Dodajanje komitenta ni uspelo!")
        nastavi_obrazec('komitenti_dodaj', oseba.vrednosti())
    redirect(url('komitenti'))


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
        nastavi_sporocilo("Urejanje komitenta ni uspelo!")
        nastavi_obrazec(f'komitenti_uredi{emso}', oseba.vrednosti())
        redirect(url('komitenti_uredi', emso=emso))
    redirect(url('komitenti'))


@post('/komitenti/izbrisi/<emso>/')
def komitenti_izbrisi_post(emso):
    try:
        Oseba.izbrisi_id(emso)
    except ValueError:
        nastavi_sporocilo("Brisanje komitenta ni uspelo!")
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
    except ValueError:
        nastavi_sporocilo("Brisanje kraja ni uspelo!")
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


@post('/racuni/<emso>/dodaj/')
def racuni_dodaj_post(emso):
    racun = Racun.ustvari(oseba_id=emso)
    try:
        racun.shrani()
    except (TypeError, ValueError):
        nastavi_sporocilo("Dodajanje računa ni uspelo!")
    redirect(url('racuni_osebe', emso=emso))


@post('/racuni/izbrisi/<stevilka:int>/')
def racuni_izbrisi_post(stevilka):
    racun = Racun.NULL
    try:
        racun = Racun.z_id(stevilka)
        racun.izbrisi()
    except ValueError:
        nastavi_sporocilo("Brisanje računa ni uspelo!")
    if racun:
        redirect(url('racuni_osebe', emso=racun.oseba_id.emso))
    else:
        redirect(url('racuni'))


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


@get('/transakcije/<stevilka:int>/dodaj/')
@view('transakcije_dodaj.html')
def transakcije_dodaj(stevilka):
    return dict(racun=Racun.z_id(stevilka))


@post('/transakcije/<stevilka:int>/dodaj/')
def transakcije_dodaj_post(stevilka):
    znesek = request.forms.getunicode('znesek')
    opis = request.forms.getunicode('opis') or None
    transakcija = Transakcija.ustvari(znesek=znesek, racun_id=stevilka, opis=opis)
    try:
        transakcija.shrani()
    except (TypeError, ValueError):
        nastavi_sporocilo("Dodajanje transakcije ni uspelo!")
        nastavi_obrazec(f'transakcije_dodaj{stevilka}', transakcija.vrednosti())
    redirect(url('transakcije_na_racunu', stevilka=stevilka))


@get('/transakcije/uredi/<id:int>/')
@view('transakcije_uredi.html')
def transakcije_uredi(id):
    return dict(transakcija=Transakcija.z_id(id))


@post('/transakcije/uredi/<id:int>/')
def transakcije_uredi_post(id):
    transakcija = Transakcija.NULL
    znesek = request.forms.getunicode('znesek')
    cas = request.forms.getunicode('cas')
    opis = request.forms.getunicode('opis') or None
    try:
        transakcija = Transakcija.z_id(id)
        transakcija.znesek = znesek
        transakcija.cas = cas
        transakcija.opis = opis
        transakcija.shrani()
    except (TypeError, ValueError):
        nastavi_sporocilo("Urejanje transakcije ni uspelo!")
        nastavi_obrazec(f'transakcije_uredi{id}', transakcija.vrednosti())
        redirect(url('transakcije_uredi', id=id))
    redirect(url('transakcije_na_racunu', stevilka=transakcija['racun_id']))


@post('/transakcije/izbrisi/<id:int>/')
def transakcije_izbrisi_post(id):
    transakcija = Transakcija.NULL
    try:
        transakcija = Transakcija.z_id(id)
        transakcija.izbrisi()
    except ValueError:
        nastavi_sporocilo("Brisanje transakcije ni uspelo!")
    if transakcija:
        redirect(url('transakcije_na_racunu', stevilka=transakcija['racun_id']))
    else:
        redirect(url('transakcije'))


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
