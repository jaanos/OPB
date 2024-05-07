from bottleext import get, post, view, run, request, response, template, \
    redirect, static_file, abort, url, debug, BaseTemplate
from model import Kraj, Oseba, Racun, Transakcija, vzpostavi_povezavo
from functools import wraps
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


def prijavljeni_uporabnik():
    """
    Vrni prijavljenega uporabnika z ID-jem iz piškotka.
    """
    emso = request.get_cookie('uporabnik', secret=SKRIVNOST)
    return Oseba.z_id(emso)


def prijavi_uporabnika(uporabnik, geslo, piskotek=None):
    """
    Nastavi piškotek na podanega uporabnika.
    """
    if not uporabnik or not uporabnik.preveri_geslo(geslo):
        nastavi_sporocilo("Prijava ni bila uspešna!")
        if piskotek:
            nastavi_obrazec(piskotek, uporabnik.vrednosti())
        redirect(url('prijava'))
    response.set_cookie('uporabnik', uporabnik.emso,
                                secret=SKRIVNOST, path='/')
    redirect(url('index'))


def odjavi_uporabnika():
    """
    Pobriši piškotek z ID-jem prijavljenega uporabnika.
    """
    izbrisi_piskotek('uporabnik')
    redirect(url('index'))


def status(preveri):
    """
    Vrni dekorator, ki preveri prijavljenega uporabnika v skladu s podano
    funkcijo in elemente vrnjenega zaporedja preda kot začetne argumente
    dekorirani funkciji.
    """
    @wraps(preveri)
    def decorator(fun):
        @wraps(fun)
        def wrapper(*largs, **kwargs):
            uporabnik = prijavljeni_uporabnik()
            out = fun(*preveri(uporabnik), *largs, **kwargs)
            if out is None:
                out = {}
            if isinstance(out, dict):
                out['uporabnik'] = uporabnik
            return out
        return wrapper
    return decorator


@status
def admin(uporabnik):
    """
    Preveri, ali ima uporabnik administratorske pravice.

    Dekorirana funkcija kot prvi argument sprejme prijavljenega uporabnika.
    """
    if not uporabnik.admin:
        abort(401, "Dostop prepovedan!")
    return (uporabnik, )


@status
def prijavljen(uporabnik):
    """
    Preveri, ali je uporabnik prijavljen.

    Dekorirana funkcija kot prvi argument sprejme prijavljenega uporabnika.
    """
    if not uporabnik:
        redirect(url('prijava'))
    return (uporabnik, )


@status
def odjavljen(uporabnik):
    """
    Preveri, ali je uporabnik odjavljen.
    """
    if uporabnik:
        redirect(url('index'))
    return ()


def preveri_lastnika(uporabnik, emso):
    """
    Preveri, ali ima prijavljeni uporabnik dovoljenje dostopa za podani EMŠO.
    """
    if uporabnik.emso != emso and not uporabnik.admin:
        abort(401, "Dostop prepovedan!")


@get('/static/<filename:path>')
def static(filename):
    return static_file(filename, root='static')


@get('/')
@view('index.html')
def index():
    pass


############################################
### Komitenti
############################################

@get('/komitenti/')
@view('komitenti.html')
@admin
def komitenti(uporabnik):
    return dict(komitenti=Oseba.seznam())


@get('/komitenti/dodaj/')
@view('komitenti_dodaj.html')
@admin
def komitenti_dodaj(uporabnik):
    pass


@post('/komitenti/dodaj/')
@admin
def komitenti_dodaj_post(uporabnik):
    emso = request.forms.getunicode('emso')
    ime = request.forms.getunicode('ime')
    priimek = request.forms.getunicode('priimek')
    naslov = request.forms.getunicode('naslov')
    kraj_id = request.forms.getunicode('kraj_id')
    up_ime = request.forms.getunicode('up_ime')
    geslo = request.forms.getunicode('geslo')
    geslo2 = request.forms.getunicode('geslo2')
    if geslo != geslo2:
        nastavi_sporocilo("Gesli se ne ujemata!")
        redirect(url('komitenti_dodaj'))
    oseba = Oseba.ustvari(ime, priimek, emso, naslov, kraj_id, up_ime)
    oseba.nastavi_geslo(geslo)
    try:
        oseba.shrani()
    except (TypeError, ValueError):
        nastavi_sporocilo("Dodajanje komitenta ni uspelo!")
        nastavi_obrazec('komitenti_dodaj', oseba.vrednosti())
    redirect(url('komitenti'))


@get('/komitenti/uredi/<emso>/')
@view('komitenti_uredi.html')
@prijavljen
def komitenti_uredi(uporabnik, emso):
    preveri_lastnika(uporabnik, emso)
    return dict(oseba=Oseba.z_id(emso))


@post('/komitenti/uredi/<emso>/')
@prijavljen
def komitenti_uredi_post(uporabnik, emso):
    preveri_lastnika(uporabnik, emso)
    nov_emso = request.forms.getunicode('emso')
    ime = request.forms.getunicode('ime')
    priimek = request.forms.getunicode('priimek')
    naslov = request.forms.getunicode('naslov')
    kraj_id = request.forms.getunicode('kraj_id')
    geslo = request.forms.getunicode('geslo')
    geslo2 = request.forms.getunicode('geslo2')
    if geslo != geslo2:
        nastavi_sporocilo("Gesli se ne ujemata!")
        redirect(url('komitenti_uredi', emso=emso))
    oseba = Oseba(ime, priimek, emso, naslov, kraj_id)
    oseba.emso = nov_emso
    if geslo:
        oseba.nastavi_geslo(geslo)
    try:
        oseba.shrani()
    except (TypeError, ValueError):
        nastavi_sporocilo("Urejanje komitenta ni uspelo!")
        nastavi_obrazec(f'komitenti_uredi{emso}', oseba.vrednosti())
        redirect(url('komitenti_uredi', emso=emso))
    if uporabnik.admin:
        redirect(url('komitenti'))
    else:
        redirect(url('index'))


@post('/komitenti/izbrisi/<emso>/')
@admin
def komitenti_izbrisi_post(uporabnik, emso):
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
@admin
def kraji(uporabnik):
    return dict(kraji=Kraj.seznam())


@post('/kraji/dodaj/')
@admin
def kraji_dodaj_post(uporabnik):
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
@admin
def kraji_uredi(uporabnik, posta):
    return dict(kraj=Kraj.z_id(posta))


@post('/kraji/uredi/<posta:int>/')
@admin
def kraji_uredi_post(uporabnik, posta):
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
@admin
def kraji_izbrisi_post(uporabnik, posta):
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
@admin
def racuni(uporabnik):
    return dict(racuni=Racun.seznam())


@get('/racuni/<emso>/')
@view('racuni_osebe.html')
@prijavljen
def racuni_osebe(uporabnik, emso):
    preveri_lastnika(uporabnik, emso)
    return dict(oseba=Oseba.z_id(emso))


@post('/racuni/<emso>/dodaj/')
@prijavljen
def racuni_dodaj_post(uporabnik, emso):
    preveri_lastnika(uporabnik, emso)
    racun = Racun.ustvari(oseba_id=emso)
    try:
        racun.shrani()
    except (TypeError, ValueError):
        nastavi_sporocilo("Dodajanje računa ni uspelo!")
    redirect(url('racuni_osebe', emso=emso))


@post('/racuni/izbrisi/<stevilka:int>/')
@prijavljen
def racuni_izbrisi_post(uporabnik, stevilka):
    racun = Racun.NULL
    try:
        racun = Racun.z_id(stevilka)
        preveri_lastnika(uporabnik, racun.oseba_id.emso)
        racun.izbrisi()
    except ValueError:
        preveri_lastnika(uporabnik, racun.oseba_id.emso)
        nastavi_sporocilo("Brisanje računa ni uspelo!")
    if racun:
        redirect(url('racuni_osebe', emso=racun.oseba_id.emso))
    elif uporabnik.admin:
        redirect(url('racuni'))
    else:
        redirect(url('index'))


############################################
### Transakcije
############################################

@get('/transakcije/')
@view('transakcije.html')
@admin
def transakcije(uporabnik):
    return dict(transakcije=Transakcija.seznam())


@get('/transakcije/<stevilka>/')
@view('transakcije_na_racunu.html')
@prijavljen
def transakcije_na_racunu(uporabnik, stevilka):
    racun = Racun.z_id(stevilka)
    preveri_lastnika(uporabnik, racun.oseba_id.emso)
    return dict(racun=racun)


@get('/transakcije/<stevilka:int>/dodaj/')
@view('transakcije_dodaj.html')
@prijavljen
def transakcije_dodaj(uporabnik, stevilka):
    racun = Racun.z_id(stevilka)
    preveri_lastnika(uporabnik, racun.oseba_id.emso)
    return dict(racun=racun)


@post('/transakcije/<stevilka:int>/dodaj/')
@prijavljen
def transakcije_dodaj_post(uporabnik, stevilka):
    racun = Racun.z_id(stevilka)
    preveri_lastnika(uporabnik, racun.oseba_id.emso)
    znesek = request.forms.getunicode('znesek')
    opis = request.forms.getunicode('opis') or None
    transakcija = Transakcija.ustvari(znesek=znesek, racun_id=racun, opis=opis)
    try:
        transakcija.shrani()
    except (TypeError, ValueError):
        nastavi_sporocilo("Dodajanje transakcije ni uspelo!")
        nastavi_obrazec(f'transakcije_dodaj{stevilka}', transakcija.vrednosti())
        redirect(url('transakcije_dodaj', stevilka=stevilka))
    redirect(url('transakcije_na_racunu', stevilka=stevilka))


@get('/transakcije/uredi/<id:int>/')
@view('transakcije_uredi.html')
@admin
def transakcije_uredi(uporabnik, id):
    return dict(transakcija=Transakcija.z_id(id))


@post('/transakcije/uredi/<id:int>/')
@admin
def transakcije_uredi_post(uporabnik, id):
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
@admin
def transakcije_izbrisi_post(uporabnik, id):
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


@get('/prijava/')
@view('prijava.html')
@odjavljen
def prijava():
    pass


@post('/prijava/')
@odjavljen
def prijava_post():
    up_ime = request.forms.getunicode('up_ime')
    geslo = request.forms.getunicode('geslo')
    uporabnik = Oseba.z_uporabniskim_imenom(up_ime)
    prijavi_uporabnika(uporabnik, geslo, 'prijava')


@post('/odjava/')
@prijavljen
def odjava_post(uporabnik):
    odjavi_uporabnika()


BaseTemplate.defaults.update(
    Kraj=Kraj,
    Oseba=Oseba,
    Racun=Racun,
    Transakcija=Transakcija,
    preberi_sporocilo=preberi_sporocilo,
    preberi_obrazec=preberi_obrazec,
    prijavljeni_uporabnik=prijavljeni_uporabnik
)

with vzpostavi_povezavo():
    # reloader=True nam olajša razvoj (osveževanje sproti - razvoj)
    run(host='localhost', port=SERVER_PORT, reloader=RELOADER)
