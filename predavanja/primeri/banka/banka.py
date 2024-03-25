from bottle import *
from model import Kraj, Oseba, Racun, Transakcija, vzpostavi_povezavo

# Odkomentiraj, če želiš sporočila o napakah
debug(True) # za izpise pri razvoju


@get('/')
def index():
    return 'Začetna stran'


############################################
### Komitent
############################################

@get('/komitenti/')
def komitenti():
    return template('komitenti.html', komitenti=Oseba.seznam())


############################################
### Kraji
############################################

@get('/kraji/')
def kraji():
    return template('kraji.html', kraji=Kraj.seznam())


@post('/kraji/dodaj/')
def kraji_dodaj_post():
    posta = request.forms.getunicode('posta')
    kraj = request.forms.getunicode('kraj')
    Kraj.ustvari(posta, kraj).shrani()
    redirect('/kraji/')


############################################
### Računi
############################################

@get('/racuni/')
def racuni():
    return template('racuni.html', racuni=Racun.seznam())


@get('/racuni/<emso>/')
def racuni_osebe(emso):
    oseba = Oseba.z_id(emso)
    return template('racuni_osebe.html', oseba=oseba)


############################################
### Transakcije
############################################

@get('/transakcije/')
def transakcije():
    return template('transakcije.html', transakcije=Transakcija.seznam())

@get('/transakcije/<stevilka>/')
def transakcije_na_racunu(stevilka):
    racun = Racun.z_id(stevilka)
    return template('transakcije_na_racunu.html', racun=racun)


with vzpostavi_povezavo():
    # reloader=True nam olajša razvoj (osveževanje sproti - razvoj)
    run(host='localhost', port=8080, reloader=True)
