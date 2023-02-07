#!/usr/bin/env python3

import sqlite3
import bottle
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import test
from pomozne import *

######################################################################
# Konfiguracija

# Vklopi debug, da se bodo predloge same osvežile in da bomo dobivali
# lepa sporočila o napakah.
bottle.debug(True)

# Datoteka, v kateri je baza
baza_datoteka = 'sqlite:///:memory:'   # podatkovna baza v spominu
# Generiranje podatkovne baze na novo

# Izpisi SQL stavkov za preverjanje delovanja
SQLAlchemyDebug = False

# priklop na podatkovno bazo
engine = create_engine(baza_datoteka, echo=SQLAlchemyDebug)  

# inicializacija generatorja sej
session = sessionmaker()
session.configure(bind=engine)

# Mapa s statičnimi datotekami
static_dir = "./static"

# Skrivnost za kodiranje cookijev
secret = "to skrivnost je zelo tezko uganiti 1094107c907cw982982c42"

resetDatabase = True

if resetDatabase:
    test.generiraj(engine, session)


######################################################################
# Pomozne funkcije

def get_user(auto_login = True, secret="", session=None):
    """Poglej cookie in ugotovi, kdo je prijavljeni uporabnik,
       vrni njegov username in ime. Če ni prijavljen, presumeri
       na stran za prijavo ali vrni None (advisno od auto_login).
    """
    # Dobimo username iz piškotka
    username = bottle.request.get_cookie('username', secret=secret)
    # Preverimo, ali ta uporabnik obstaja
    if username is not None:
        try:
            u = session.query(Uporabnik).filter(Uporabnik.username == username).one()
            return u
        except:
            print("Nismo našli uporabnika.")
        finally:
            session.close()
    if auto_login:
        print("Autologin...")
        bottle.redirect('/login/')
    else: return None
        
        
def traci(limit=10, session=None):
    """Vrni dano število tračev (privzeto 10). Rezultat je seznam, katerega
       elementi so oblike [trac_id, avtor, ime_avtorja, cas_objave, vsebina, komentarji],
       pri čemer so komentarji seznam elementov oblike [avtor, ime_avtorja, vsebina],
       urejeni po času objave.
    """

##"""SELECT trac.id, username, ime, komentar.vsebina
##FROM
##(komentar JOIN trac ON komentar.trac = trac.id)
##JOIN uporabnik ON uporabnik.username = komentar.avtor
##WHERE
##trac.id IN (SELECT id FROM trac ORDER BY cas DESC LIMIT ?)
##ORDER BY
##komentar.cas""", [limit])
    
    trc = session.query(Trac).order_by(Trac.cas).limit(limit)
    return [(tr.id, tr.avtor.username, tr.avtor.ime, pretty_date(tr.cas),
                 tr.vsebina, [(k.avtor.username, k.avtor.ime, k.vsebina) for k in tr.komentarji]) for tr in trc]


######################################################################
# Funkcije, ki obdelajo zahteve odjemalcev.

@bottle.route("/static/<filename:path>")
def static(filename):
    """Splošna funkcija, ki servira vse statične datoteke iz naslova
       /static/..."""
    return bottle.static_file(filename, root=static_dir)

@bottle.route("/")
def main():
    """Glavna stran."""
    # Iz cookieja dobimo uporabnika (ali ga preusmerimo na login, če
    # nima cookija)
    s = session()
    u = get_user(secret=secret, session=s)
    # Morebitno sporočilo za uporabnika
    sporocilo = get_sporocilo(secret)
    print("Sporocilo:", type(sporocilo))
    # Seznam zadnjih 10 tračev
    ts = traci(session=s)
    # Vrnemo predlogo za glavno stran
    print(u.ime, u.username, ts, sporocilo)
    return bottle.template("main.html",
                           ime=u.ime,
                           username=u.username,
                           traci=ts,
                           sporocilo=sporocilo)

@bottle.get("/login/")
def login_get():
    """Serviraj formo za login."""
    return bottle.template("login.html",
                           napaka=None,
                           username=None)

@bottle.get("/logout/")
def logout():
    """Pobriši cookie in preusmeri na login."""
    print("Brišem cookie")
    bottle.response.delete_cookie('username', path="/")
    bottle.redirect('/login/')

@bottle.post("/login/")
def login_post():
    """Obdelaj izpolnjeno formo za prijavo"""
    # Uporabniško ime, ki ga je uporabnik vpisal v formo
    username = bottle.request.forms.username
    # Izračunamo MD5 has gesla, ki ga bomo spravili
    password = password_md5(bottle.request.forms.password)
    # Preverimo, ali se je uporabnik pravilno prijavil
    s = session()
    try:
        u = s.query(Uporabnik).filter(Uporabnik.username==username, Uporabnik.password==password).one()
        print(u.username, u.password)
    except:
        # Username in geslo se ne ujemata
        return bottle.template("login.html",
                               napaka="Nepravilna prijava",
                               username=username)
    # Vse je v redu, nastavimo cookie in preusmerimo na glavno stran
    bottle.response.set_cookie('username', u.username, path='/', secret=secret)
    print("Redirecting")
    bottle.redirect("/")


@bottle.get("/register/")
def login_get():
    """Prikaži formo za registracijo."""
    return bottle.template("register.html", 
                           username=None,
                           ime=None,
                           napaka=None)

@bottle.post("/register/")
def register_post():
    """Registriraj novega uporabnika."""
    username = bottle.request.forms.username
    ime = bottle.request.forms.ime
    password1 = bottle.request.forms.password1
    password2 = bottle.request.forms.password2
    # Ali uporabnik že obstaja?
    s = session()
    u = None
    try:
        u = s.query(Uporabnik).filter(Uporabnik.username==username).one()
    except:
        pass

    if u is not None:
        s.close()
        return bottle.template("register.html",
                           username=username,
                           ime=ime,
                           napaka='To uporabniško ime je že zavzeto')
    
    if not password1 == password2:
        # Geslo se ne ujemata
        s.close()
        return bottle.template("register.html",
                           username=username,
                           ime=ime,
                           napaka='Gesli se ne ujemata')

    # Vse je v redu, vstavi novega uporabnika v bazo
    password = password_md5(password1)
    s.add(Uporabnik(username=username, password=password, ime=ime))
    s.commit()
    s.close()
    # Daj uporabniku cookie
    bottle.response.set_cookie('username', username, path='/', secret=secret)
    bottle.redirect("/")

@bottle.post("/trac/new/")
def new_trac():
    """Ustvari nov trač."""
    # Kdo je avtor trača?
    s = session()
    u = get_user(secret=secret, session=s)
    # Vsebina trača
    trac = bottle.request.forms.trac
    s.add(Trac(avtor=u, vsebina=trac))
    s.commit()
    s.close()
    # Presumerimo na glavno stran
    return bottle.redirect("/")

@bottle.route("/user/<username>/")
def user_wall(username, sporocila=[]):
    """Prikaži stran uporabnika"""
    # Kdo je prijavljeni uporabnik? (Ni nujno isti kot username.)
    s = session()
    prijavljeni = get_user(secret=secret, session=s)  
    # Ime uporabnika (hkrati preverimo, ali uporabnik sploh obstaja)

    trenutni = s.query(Uporabnik).filter(Uporabnik.username==username).one()
    t = s.query(Trac).filter(Trac.avtor==trenutni).count()
    k = s.query(Komentar).filter(Komentar.avtor==trenutni).count()
    s.close()
    # Prikažemo predlogo
    return bottle.template("user.html",
                           uporabnik_ime=trenutni.ime,
                           uporabnik=trenutni.username,
                           username=prijavljeni.username,
                           ime=prijavljeni.ime,
                           trac_count=t,
                           komentar_count=k,
                           sporocila=sporocila)
    
@bottle.post("/user/<username>/")
def user_change(username):
    """Obdelaj formo za spreminjanje podatkov o uporabniku."""
    # Kdo je prijavljen?
    s = session()
    prijavljeni = get_user(secret=secret, session=s)   
    # Novo ime
    ime_new = bottle.request.forms.ime
    # Staro geslo (je obvezno)
    password1 = password_md5(bottle.request.forms.password1)
    # Preverimo staro geslo
    s = session()
    sporocila = []
    u = None
    try:
        # ce se staro geslo ne ujema, ne najde uporabnika in vrze izjemo
        u = s.query(Uporabnik).filter(Uporabnik.username==prijavljeni.username, Uporabnik.password==password1).one()
    except:
        pass

    if u is None:
        sporocila.append(("alert-danger", "Napačno staro geslo"))
    else:
          # Geslo je ok
          # Ali je treba spremeniti ime?
        save = False
        if ime_new != u.ime:
            sporocila.append(("alert-success", "Spreminili ste si ime."))
            u.ime = ime_new
            save = True
        # Ali je treba spremeniti geslo?
        password2 = bottle.request.forms.password2
        password3 = bottle.request.forms.password3
        if password2 or password3:
            # Preverimo, ali se gesli ujemata
            if password2 == password3:
                # Vstavimo v bazo novo geslo
                sporocila.append(("alert-success", "Spremenili ste geslo."))
                u.password = password_md5(password2)
                save = True
            else:
                sporocila.append(("alert-danger", "Gesli se ne ujemata"))
                save = False
        if save:
            s.commit()
            s.close()
        
    # Prikažemo stran z uporabnikom, z danimi sporočili. Kot vidimo,
    # lahko kar pokličemo funkcijo, ki servira tako stran
    return user_wall(username, sporocila=sporocila)

@bottle.post("/komentar/<tid:int>/")
def komentar(tid):
    """Vnesi nov komentar."""
    s = session()
    prijavljeni = get_user(secret=secret, session=s)
##    if prijavljeni is None:
##        bottle.redirect("/login/")
    komentar = bottle.request.forms.komentar
    trac = s.query(Trac).filter(Trac.id==tid).one()
    s.add(trac.komentiraj(prijavljeni, komentar))
    s.commit()
    s.close()
    bottle.redirect("/#trac-{0}".format(tid))

@bottle.route("/trac/<tid:int>/delete/")
def komentar_delete(tid):
    """Zbriši komentar."""
    raise Exception("Še ne deluje.")
    (username, ime) = get_user(secret=secret)
    # DELETE napišemo tako, da deluje samo, če je avtor komentarja prijavljeni uporabnik
    r = baza.execute("DELETE FROM trac WHERE id=? AND avtor=?", [tid, username]).rowcount;
    if not r == 1:
        return "Vi ste hacker."
    else:
        set_sporocilo('alert-success', "Vaš komentar je IZBRISAN.", secret)
        return bottle.redirect("/")



######################################################################
# Glavni program

# priklopimo se na bazos
#baza = sqlite3.connect(baza_datoteka, isolation_level=None)

# poženemo strežnik na portu 8080, glej http://localhost:8080/
bottle.run(host='localhost', port=8080)
    
