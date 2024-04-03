from bottleext import get, post, view, run, request, template, redirect, static_file, url, debug
from model import Kraj, Oseba, Racun, Transakcija, vzpostavi_povezavo
import os


# privzete nastavitve
SERVER_PORT = os.environ.get('BOTTLE_PORT', 8080)
RELOADER = os.environ.get('BOTTLE_RELOADER', True)
DB_PORT = os.environ.get('POSTGRES_PORT', 5432)


# Odkomentiraj, če želiš sporočila o napakah
debug(True) # za izpise pri razvoju


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
    kraj = request.forms.getunicode('kraj')
    Kraj.ustvari(posta, kraj).shrani()
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


with vzpostavi_povezavo():
    # reloader=True nam olajša razvoj (osveževanje sproti - razvoj)
    run(host='localhost', port=SERVER_PORT, reloader=RELOADER)
