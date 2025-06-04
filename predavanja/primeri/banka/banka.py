from functools import wraps
from model import Entiteta, Kraj, Oseba, Racun, Transakcija, vzpostavi_povezavo
import bottle
import bottleext
import json
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


def nastavi_obrazec(piskotek, objekt):
    """
    Nastavi piškotek s polji objekta.
    """
    nastavi_piskotek(piskotek, json.dumps(objekt.slovar()))


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
    if not uporabnik or not uporabnik.preveri_geslo(geslo):
        nastavi_sporocilo("Prijava ni bila uspešna!")
        if piskotek:
            nastavi_obrazec(piskotek, uporabnik)
        bottle.redirect(bottle.url('prijava'))
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
    preberi_sporocilo=preberi_sporocilo,
    preberi_obrazec=preberi_obrazec,
    prijavljeni_uporabnik=prijavljeni_uporabnik
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
@admin
def kraji(uporabnik):
    pass


@bottle.post('/kraji/izbrisi/<posta:int>/')
@admin
def kraji_izbrisi_post(uporabnik, posta):
    try:
        Kraj.izbrisi_id(posta)
        nastavi_sporocilo(f'Kraj s poštno številko {posta} uspešno pobrisan.')
    except ValueError:
        nastavi_sporocilo(f'Brisanje kraja s poštno številko {posta} neuspešno!')
    bottle.redirect(bottle.url('kraji'))


@bottle.get('/kraji/dodaj/')
@bottle.view('kraji.dodaj.html')
@admin
def kraji_dodaj(uporabnik):
    pass


@bottle.post('/kraji/dodaj/')
@admin
def kraji_dodaj_post(uporabnik):
    posta = bottle.request.forms.getunicode('posta')
    ime = bottle.request.forms.getunicode('kraj')
    kraj = Kraj(posta, ime)
    try:
        kraj.vstavi()
        nastavi_sporocilo(f'Uspešno dodan kraj s poštno številko {posta}.')
        bottle.redirect(bottle.url('kraji'))
    except (ValueError, TypeError):
        nastavi_sporocilo(f'Dodajanje kraja s poštno številko {posta} ni uspelo!')
        nastavi_obrazec('kraji_dodaj', kraj)
        bottle.redirect(bottle.url('kraji_dodaj'))


@bottle.get('/kraji/uredi/<posta:int>/')
@bottle.view('kraji.uredi.html')
@admin
def kraji_uredi(uporabnik, posta):
    return dict(kraj=Kraj.z_id(posta))


@bottle.post('/kraji/uredi/<posta:int>/')
@admin
def kraji_uredi_post(uporabnik, posta):
    stara_posta = posta
    ime = bottle.request.forms.getunicode('kraj')
    kraj = Kraj.iz_baze(posta, ime)
    kraj.posta = bottle.request.forms.getunicode('posta')
    try:
        kraj.posodobi()
        nastavi_sporocilo(f'Uspešno posodobljen kraj s poštno številko {posta}.')
        bottle.redirect(bottle.url('kraji'))
    except (ValueError, TypeError):
        nastavi_sporocilo(f'Urejanje kraja s poštno številko {stara_posta} ni uspelo!')
        nastavi_obrazec(f'kraji_uredi_{stara_posta}', kraj)
        bottle.redirect(bottle.url('kraji_uredi', posta=stara_posta))


@bottle.get('/komitenti/')
@bottle.view('komitenti.html')
@admin
def komitenti(uporabnik):
    pass


@bottle.post('/komitenti/izbrisi/<emso>/')
@admin
def komitenti_izbrisi_post(uporabnik, emso):
    try:
        Oseba.izbrisi_id(emso)
        nastavi_sporocilo(f'Komitent z EMŠOm {emso} uspešno pobrisan.')
    except ValueError:
        nastavi_sporocilo(f'Brisanje komitenta z EMŠOm {emso} neuspešno!')
    bottle.redirect(bottle.url('komitenti'))


@bottle.get('/komitenti/dodaj/')
@bottle.view('komitenti.dodaj.html')
@admin
def komitenti_dodaj(uporabnik):
    pass


@bottle.post('/komitenti/dodaj/')
@admin
def komitenti_dodaj_post(uporabnik):
    emso = bottle.request.forms.getunicode('emso')
    ime = bottle.request.forms.getunicode('ime')
    priimek = bottle.request.forms.getunicode('priimek')
    naslov = bottle.request.forms.getunicode('naslov')
    kraj = bottle.request.forms.getunicode('kraj')
    up_ime = bottle.request.forms.getunicode('up_ime')
    geslo = bottle.request.forms.getunicode('geslo')
    geslo2 = bottle.request.forms.getunicode('geslo2')
    admin = bottle.request.forms.getunicode('admin')
    try:
        kraj = int(kraj)
    except ValueError:
        pass
    oseba = Oseba(emso, ime, priimek, naslov, kraj, up_ime, admin=admin)
    if geslo or geslo2:
        if geslo != geslo2:
            nastavi_sporocilo("Gesli se ne ujemata!")
            nastavi_obrazec('komitenti_dodaj', oseba)
            bottle.redirect(bottle.url('komitenti_dodaj'))
        oseba.nastavi_geslo(geslo)
    try:
        oseba.vstavi()
        nastavi_sporocilo(f'Uspešno dodan komitent z EMŠOm {emso}.')
        bottle.redirect(bottle.url('komitenti'))
    except (ValueError, TypeError):
        nastavi_sporocilo(f'Dodajanje komitenta z EMŠOm {emso} ni uspelo!')
        nastavi_obrazec('komitenti_dodaj', oseba)
        bottle.redirect(bottle.url('komitenti_dodaj'))


@bottle.get('/komitenti/uredi/<emso>/')
@bottle.view('komitenti.uredi.html')
@prijavljen
def komitenti_uredi(uporabnik, emso):
    preveri_lastnika(uporabnik, emso)
    return dict(oseba=Oseba.z_id(emso))


@bottle.post('/komitenti/uredi/<emso>/')
@prijavljen
def komitenti_uredi_post(uporabnik, emso):
    preveri_lastnika(uporabnik, emso)
    ime = bottle.request.forms.getunicode('ime')
    priimek = bottle.request.forms.getunicode('priimek')
    naslov = bottle.request.forms.getunicode('naslov')
    kraj = bottle.request.forms.getunicode('kraj')
    up_ime = bottle.request.forms.getunicode('up_ime')
    geslo = bottle.request.forms.getunicode('geslo')
    geslo2 = bottle.request.forms.getunicode('geslo2')
    try:
        kraj = int(kraj)
    except ValueError:
        pass
    oseba = Oseba.z_id(emso)
    oseba.posodobi_polja(ime=ime, priimek=priimek, naslov=naslov, kraj=kraj,
                         up_ime=up_ime)
    if uporabnik.admin:
        oseba.admin = bool(bottle.request.forms.getunicode('admin'))
    if geslo or geslo2:
        if geslo != geslo2:
            nastavi_sporocilo("Gesli se ne ujemata!")
            nastavi_obrazec('komitenti_dodaj', oseba)
            bottle.redirect(bottle.url('komitenti_uredi', emso=emso))
        oseba.nastavi_geslo(geslo)
    try:
        oseba.posodobi()
        nastavi_sporocilo(f'Uspešno posodobljen komitent z EMŠOm {emso}.')
        if uporabnik.admin:
            bottle.redirect(bottle.url('komitenti'))
        else:
            bottle.redirect(bottle.url('index'))
    except (ValueError, TypeError):
        nastavi_sporocilo(f'Urejanje komitenta z EMŠOm {emso} ni uspelo!')
        nastavi_obrazec(f'komitenti_uredi_{emso}', oseba)
        bottle.redirect(bottle.url('komitenti_uredi', emso=emso))


@bottle.get('/komitenti/racuni/<emso>/')
@bottle.view('komitenti.racuni.html')
@prijavljen
def komitenti_racuni(uporabnik, emso):
    preveri_lastnika(uporabnik, emso)
    oseba = Oseba.z_id(emso)
    return dict(oseba=oseba, racuni=oseba.racuni())


@bottle.get('/komitenti/transakcije/<emso>/')
@bottle.view('komitenti.transakcije.html')
@prijavljen
def komitenti_transakcije(uporabnik, emso):
    preveri_lastnika(uporabnik, emso)
    oseba = Oseba.z_id(emso)
    return dict(oseba=oseba)


@bottle.get('/racuni/')
@bottle.view('racuni.html')
@admin
def racuni(uporabnik):
    pass


@bottle.post('/racuni/izbrisi/<stevilka:int>/')
@prijavljen
def racuni_izbrisi_post(uporabnik, stevilka):
    try:
        if uporabnik.admin:
            Racun.izbrisi_id(stevilka)
        else:
            racun = Racun.z_id(stevilka)
            preveri_lastnika(uporabnik, racun['lastnik'])
            racun.izbrisi()
        nastavi_sporocilo(f'Račun s številko {stevilka} uspešno pobrisan.')
    except ValueError:
        nastavi_sporocilo(f'Brisanje računa s številko {stevilka} neuspešno!')
    if uporabnik.admin:
        bottle.redirect(bottle.url('racuni'))
    else:
        bottle.redirect(bottle.url('komitenti_racuni', emso=uporabnik.emso))


@bottle.post('/racuni/dodaj/<emso>/')
@prijavljen
def racuni_dodaj_post(uporabnik, emso):
    preveri_lastnika(uporabnik, emso)
    try:
        racun = Racun(lastnik=emso)
        racun.vstavi()
        nastavi_sporocilo(f'Uspešno dodan račun s številko {racun.stevilka}.')
    except (ValueError, TypeError):
        nastavi_sporocilo(f'Dodajanje računa za uporabnika z EMŠOm {emso} ni uspelo!')
    bottle.redirect(bottle.url('komitenti_racuni', emso=emso))


@bottle.get('/racuni/transakcije/<stevilka:int>/')
@bottle.view('racuni.transakcije.html')
@prijavljen
def racuni_transakcije(uporabnik, stevilka):
    racun = Racun.z_id(stevilka)
    preveri_lastnika(uporabnik, racun['lastnik'])
    return dict(racun=racun)


@bottle.get('/transakcije/')
@bottle.view('transakcije.html')
@admin
def transakcije(uporabnik):
    pass


@bottle.post('/transakcije/izbrisi/<id:int>/')
@admin
def transakcije_izbrisi_post(uporabnik, id):
    try:
        Transakcija.izbrisi_id(id)
        nastavi_sporocilo(f'Transakcija z ID-jem {id} uspešno pobrisana.')
    except:
        nastavi_sporocilo(f'Brisanje transakcije z ID-jem {id} neuspešno!')
    bottle.redirect(bottle.url('transakcije'))


@bottle.get('/transakcije/dodaj/<stevilka:int>/')
@bottle.view('transakcije.dodaj.html')
@prijavljen
def transakcije_dodaj(uporabnik, stevilka):
    racun = Racun.z_id(stevilka)
    preveri_lastnika(uporabnik, racun['lastnik'])
    return dict(racun=racun)


@bottle.post('/transakcije/dodaj/<stevilka:int>/')
@prijavljen
def transakcije_dodaj_post(uporabnik, stevilka):
    racun = Racun.z_id(stevilka)
    preveri_lastnika(uporabnik, racun['lastnik'])
    znesek = bottle.request.forms.getunicode('znesek')
    cas = bottle.request.forms.getunicode('cas')
    opis = bottle.request.forms.getunicode('opis')
    transakcija = Transakcija(racun=racun, znesek=znesek, cas=cas, opis=opis)
    try:
        transakcija.vstavi()
        nastavi_sporocilo(f'Uspešno dodana transakcija z ID-jem {transakcija.id}.')
        bottle.redirect(bottle.url('racuni_transakcije', stevilka=stevilka))
    except (ValueError, TypeError):
        nastavi_sporocilo(f'Dodajanje transakcije na računu s številko {stevilka} ni uspelo!')
        nastavi_obrazec(f'racuni_dodaj_{stevilka}', transakcija)
        bottle.redirect(bottle.url('racuni_transakcije', stevilka=stevilka))


@bottle.get('/transakcije/uredi/<id:int>/')
@bottle.view('transakcije.uredi.html')
@admin
def transakcije_uredi(uporabnik, id):
    transakcija = Transakcija.z_id(id)
    transakcija.racun = Racun.z_id(transakcija['racun'])
    return dict(transakcija=transakcija)


@bottle.post('/transakcije/uredi/<id:int>/')
@admin
def transakcije_uredi_post(uporabnik, id):
    transakcija = Transakcija.z_id(id)
    transakcija.znesek = bottle.request.forms.getunicode('znesek')
    transakcija.cas = bottle.request.forms.getunicode('cas')
    transakcija.opis = bottle.request.forms.getunicode('opis')
    try:
        transakcija.posodobi()
        nastavi_sporocilo(f'Uspešno posodobljena transakcija z ID-jem {id}.')
        bottle.redirect(bottle.url('transakcije'))
    except (ValueError, TypeError):
        nastavi_sporocilo(f'Urejanje transakcije z ID-jem {id} ni uspelo!')
        nastavi_obrazec(f'transakcije_uredi_{id}', transakcija)
        bottle.redirect(bottle.url('transakcije_uredi', id=id))


@bottle.get('/prijava/')
@bottle.view('prijava.html')
@odjavljen
def prijava():
    pass


@bottle.post('/prijava/')
@odjavljen
def prijava_post():
    up_ime = bottle.request.forms.getunicode('up_ime')
    geslo = bottle.request.forms.getunicode('geslo')
    uporabnik = Oseba.z_uporabniskim_imenom(up_ime)
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
    up_ime = bottle.request.forms.getunicode('up_ime')
    geslo = bottle.request.forms.getunicode('geslo')
    geslo2 = bottle.request.forms.getunicode('geslo2')
    uporabnik = Oseba(emso, ime, priimek, naslov, kraj, up_ime)
    if geslo != geslo2:
        nastavi_sporocilo("Gesli se ne ujemata!")
        nastavi_obrazec('registracija', uporabnik)
        bottle.redirect(bottle.url('registracija'))
    uporabnik.nastavi_geslo(geslo)
    try:
        uporabnik.vstavi()
    except (TypeError, ValueError):
        nastavi_sporocilo("Dodajanje uporabnika ni uspelo!")
        nastavi_obrazec('registracija', uporabnik)
        bottle.redirect(bottle.url('registracija'))
    prijavi_uporabnika(uporabnik, geslo, 'registracija')


@bottle.post('/odjava/')
@prijavljen
def odjava_post(uporabnik):
    odjavi_uporabnika()


with vzpostavi_povezavo(port=DB_PORT):
    # reloader=True nam olajša razvoj (osveževanje sproti - razvoj)
    bottle.run(host='localhost', port=SERVER_PORT, reloader=RELOADER)
