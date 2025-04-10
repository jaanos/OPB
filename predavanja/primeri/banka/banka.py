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


bottle.BaseTemplate.defaults.update(
    Kraj=Kraj,
    Oseba=Oseba,
    Racun=Racun,
    Transakcija=Transakcija,
    url=bottle.url
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


@bottle.get('/komitenti/')
@bottle.view('komitenti.html')
def komitenti():
    pass


@bottle.get('/racuni/')
@bottle.view('racuni.html')
def racuni():
    pass


@bottle.get('/transakcije/')
@bottle.view('transakcije.html')
def transakcije():
    pass


with vzpostavi_povezavo(port=DB_PORT):
    # reloader=True nam olajša razvoj (osveževanje sproti - razvoj)
    bottle.run(host='localhost', port=SERVER_PORT, reloader=RELOADER)
