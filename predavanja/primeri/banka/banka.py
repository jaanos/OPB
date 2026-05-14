from functools import wraps
from model import Entiteta, Kraj, Oseba, Racun, Transakcija, IntegrityError, vzpostavi_povezavo
import bottle
import bottleext
import json
import os


# privzete nastavitve
SERVER_PORT = os.environ.get('BOTTLE_PORT', 8080)
RELOADER = os.environ.get('BOTTLE_RELOADER', True)
DB_PORT = os.environ.get('POSTGRES_PORT', 5432)
SKRIVNOST = 'nekaj, kar bo zelo težko uganiti!!!!  fndkdfvdkbvtzuj hbjh'


# Odkomentiraj, če želiš sporočila o napakah
bottle.debug(True) # za izpise pri razvoju


def nastavi_piskotek(piskotek, vsebina):
    """
    Nastavi podani piškotek.
    """
    bottle.response.set_cookie(piskotek, vsebina, secret=SKRIVNOST, path='/')


def preberi_piskotek(piskotek, izbrisi=False):
    """
    Preberi podani piškotek.
    """
    if izbrisi:
        pobrisi_piskotek(piskotek)
    return bottle.request.get_cookie(piskotek, secret=SKRIVNOST)


def pobrisi_piskotek(piskotek):
    """
    Pobriši podani piškotek.
    """
    bottle.response.delete_cookie(piskotek, path='/')


def nastavi_sporocilo(sporocilo):
    """
    Nastavi podano sporočilo.
    """
    nastavi_piskotek('sporocilo', sporocilo)


def preberi_sporocilo():
    """
    Vrni sporočilo in pobriši piškotek.
    """
    return preberi_piskotek('sporocilo', izbrisi=True)


def nastavi_obrazec(piskotek, objekt):
    """
    Nastavi piškotek s polji objekta.
    """
    nastavi_piskotek(piskotek, json.dumps(objekt.kot_slovar()))


def preberi_obrazec(piskotek, obj):
    """
    Vrni objekt iz piškotka in ga pobriši.
    """
    try:
        slovar = json.loads(preberi_piskotek(piskotek, izbrisi=True))
        if isinstance(obj, Entiteta):
            obj.posodobi_polja(**slovar)
            return obj
        else:
            return obj(**slovar)
    except (TypeError, json.JSONDecodeError):
        return obj if isinstance(obj, Entiteta) else obj.NULL


def prijavljeni_uporabnik():
    """
    Vrni prijavljenega uporabnika z ID-jem iz piškotka.
    """
    try:
        return Oseba.z_id(preberi_piskotek('uporabnik'))
    except ValueError:
        return Oseba.NULL


def prijavi_uporabnika(uporabnik, geslo, piskotek=None):
    """
    Nastavi piškotek na podanega uporabnika.
    """
    if not uporabnik or not uporabnik.prijavi(geslo):
        nastavi_sporocilo("Prijava ni bila uspešna!")
        if piskotek:
            nastavi_obrazec(piskotek, uporabnik)
        bottle.redirect(bottle.url('prijava'))
    print(uporabnik.emso, type(uporabnik.emso))
    nastavi_piskotek('uporabnik', uporabnik.emso)
    bottle.redirect(bottle.url('index'))


def odjavi_uporabnika():
    """
    Pobriši piškotek z ID-jem prijavljenega uporabnika.
    """
    pobrisi_piskotek('uporabnik')
    bottle.redirect(bottle.url('index'))


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
        bottle.abort(401, "Dostop prepovedan!")
    return (uporabnik, )


@status
def prijavljen(uporabnik):
    """
    Preveri, ali je uporabnik prijavljen.

    Dekorirana funkcija kot prvi argument sprejme prijavljenega uporabnika.
    """
    if not uporabnik:
        bottle.redirect(bottle.url('prijava'))
    return (uporabnik, )


@status
def odjavljen(uporabnik):
    """
    Preveri, ali je uporabnik odjavljen.
    """
    if uporabnik:
        bottle.redirect(bottle.url('index'))
    return ()


def preveri_lastnika(uporabnik, emso):
    """
    Preveri, ali ima prijavljeni uporabnik dovoljenje dostopa za podani EMŠO.
    """
    if uporabnik.emso != emso and not uporabnik.admin:
        bottle.abort(401, "Dostop prepovedan!")


bottle.BaseTemplate.defaults.update(
    Kraj=Kraj,
    Oseba=Oseba,
    Racun=Racun,
    Transakcija=Transakcija,
    url=bottle.url,
    urlencode=bottle.urlencode,
    preberi_sporocilo=preberi_sporocilo,
    preberi_obrazec=preberi_obrazec,
    prijavljeni_uporabnik=prijavljeni_uporabnik,
)


@bottle.get('/static/<filename:path>')
def static(filename):
    return bottle.static_file(filename, root='static')


@bottle.get('/')
@bottle.view('index.html')
def index():
    pass


@bottle.get('/prijava/')
@bottle.view('prijava.html')
@odjavljen
def prijava():
    pass


@bottle.post('/prijava/')
@odjavljen
def prijava_post():
    uporabnisko_ime = bottle.request.forms.getunicode('uporabnisko_ime')
    geslo = bottle.request.forms.getunicode('geslo')
    uporabnik = Oseba.z_uporabniskim_imenom(uporabnisko_ime)
    prijavi_uporabnika(uporabnik, geslo, 'prijava')


@bottle.get('/registracija/')
@bottle.view('registracija.html')
@odjavljen
def registracija():
    pass


@bottle.post('/registracija/')
@odjavljen
def registracija_post():
    emso = bottle.request.forms.getunicode('emso')
    ime = bottle.request.forms.getunicode('ime')
    priimek = bottle.request.forms.getunicode('priimek')
    naslov = bottle.request.forms.getunicode('naslov')
    kraj = bottle.request.forms.getunicode('kraj')
    uporabnisko_ime = bottle.request.forms.getunicode('uporabnisko_ime')
    geslo = bottle.request.forms.getunicode('geslo')
    geslo2 = bottle.request.forms.getunicode('geslo2')
    uporabnik = Oseba(emso, ime, priimek, naslov, kraj, uporabnisko_ime, geslo)
    if geslo != geslo2:
        uporabnik.geslo = None
        nastavi_sporocilo("Gesli se ne ujemata!")
        nastavi_obrazec('registracija', uporabnik)
        bottle.redirect(bottle.url('registracija'))
    try:
        uporabnik.vstavi()
    except IntegrityError:
        uporabnik.geslo = None
        nastavi_sporocilo("Dodajanje uporabnika ni uspelo!")
        nastavi_obrazec('registracija', uporabnik)
        bottle.redirect(bottle.url('registracija'))
    prijavi_uporabnika(uporabnik, geslo, 'registracija')


@bottle.post('/odjava/')
@prijavljen
def odjava_post(uporabnik):
    odjavi_uporabnika()


with vzpostavi_povezavo(port=DB_PORT):
    bottle.run(host='localhost', port=SERVER_PORT, reloader=RELOADER)
