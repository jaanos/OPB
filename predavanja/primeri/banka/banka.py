from model import Kraj, Oseba, Racun, Transakcija, vzpostavi_povezavo
import bottle
import bottleext
import os


# privzete nastavitve
SERVER_PORT = os.environ.get('BOTTLE_PORT', 8080)
RELOADER = os.environ.get('BOTTLE_RELOADER', True)
DB_PORT = os.environ.get('POSTGRES_PORT', 5432)
SKRIVNOST = 'nekaj, kar bo zelo težko uganiti!!!!  jvdfkv dvkh vsh'


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


bottle.BaseTemplate.defaults.update(
    Kraj=Kraj,
    Oseba=Oseba,
    Racun=Racun,
    Transakcija=Transakcija,
    url=bottle.url,
    preberi_sporocilo=preberi_sporocilo
)


@bottle.get('/static/<filename:path>')
def static(filename):
    return bottle.static_file(filename, root='static')


@bottle.get('/')
@bottle.view('index.html')
def index():
    pass


@bottle.get('/kraji/')
@bottle.view('kraji.html')
def kraji():
    pass


@bottle.post('/kraji/izbrisi/<posta:int>/')
def izbrisi_kraj(posta):
    try:
        Kraj.izbrisi_id(posta)
        nastavi_sporocilo(f'Kraj s poštno številko {posta} uspešno pobrisan.')
    except ValueError:
        nastavi_sporocilo(f'Brisanje kraja s poštno številko {posta} neuspešno!')
    bottle.redirect(bottle.url('kraji'))


@bottle.get('/komitenti/')
@bottle.view('komitenti.html')
def komitenti():
    pass


@bottle.post('/komitenti/izbrisi/<emso>/')
def izbrisi_komitenta(emso):
    try:
        Oseba.izbrisi_id(emso)
        nastavi_sporocilo(f'Komitent z EMŠOm {emso} uspešno pobrisan.')
    except ValueError:
        nastavi_sporocilo(f'Brisanje komitenta z EMŠOm {emso} neuspešno!')
    bottle.redirect(bottle.url('komitenti'))


@bottle.get('/racuni/')
@bottle.view('racuni.html')
def racuni():
    pass


@bottle.post('/racuni/izbrisi/<stevilka:int>/')
def izbrisi_racun(stevilka):
    try:
        Racun.izbrisi_id(stevilka)
        nastavi_sporocilo(f'Račun s številko {stevilka} uspešno pobrisan.')
    except:
        nastavi_sporocilo(f'Brisanje računa s številko {stevilka} neuspešno!')
    bottle.redirect(bottle.url('racuni'))


@bottle.get('/transakcije/')
@bottle.view('transakcije.html')
def transakcije():
    pass


@bottle.post('/transakcije/izbrisi/<id:int>/')
def izbrisi_transakcijo(id):
    try:
        Transakcija.izbrisi_id(id)
        nastavi_sporocilo(f'Transakcija z ID-jem {id} uspešno pobrisana.')
    except:
        nastavi_sporocilo(f'Brisanje transakcije z ID-jem {id} neuspešno!')
    bottle.redirect(bottle.url('transakcije'))


with vzpostavi_povezavo(port=DB_PORT):
    # reloader=True nam olajša razvoj (osveževanje sproti - razvoj)
    bottle.run(host='localhost', port=SERVER_PORT, reloader=RELOADER)
