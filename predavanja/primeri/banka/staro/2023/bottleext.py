import os
import bottle
import sqlite3
import bcrypt
from bottle import *
from functools import wraps


# KONFIGURACIJA
SERVER_HOST = os.environ.get('BOTTLE_HOST', 'localhost')
SERVER_PORT = os.environ.get('BOTTLE_PORT', 8080)
SERVER_ROOT = os.environ.get('BOTTLE_ROOT', '')
RELOADER = os.environ.get('BOTTLE_RELOADER', True)
SKRIVNOST = os.environ.get('BOTTLE_SECRET', "rODX3ulHw3ZYRdbIVcp1IfJTDn8iQTH6TFaNBgrSkjIulr")
BAZA = 'banka.db'
STATIC_ROOT = "./static"

def nastavi_geslo(geslo):
    geslo = geslo.encode("utf-8")
    sol = bcrypt.gensalt()
    return bcrypt.hashpw(geslo, sol)


def preveri_geslo(geslo, zgostitev):
    geslo = geslo.encode("utf-8")
    return bcrypt.checkpw(geslo, zgostitev)


class Route(bottle.Route):
    """
    Nadomestni razred za poti s privzetimi imeni.
    """
    def __init__(self, app, rule, method, callback, name=None, plugins=None, skiplist=None, **config):
        if name is None:
            name = callback.__name__

        @wraps(callback)
        def decorator(*largs, **kwargs):
            bottle.request.environ['SCRIPT_NAME'] = SERVER_ROOT
            emso = request.get_cookie("uporabnik", secret=SKRIVNOST)
            try:
                cur = baza.cursor()
                uporabnik = Uporabnik(cur, emso)
                return callback(uporabnik, cur, *largs, **kwargs)
            finally:
                cur.close()

        super().__init__(app, rule, method, decorator, name, plugins, skiplist, **config)


class Uporabnik:
    def __init__(self, cur, emso=None, up_ime=None, geslo=None, geslo2=None,
                 ime=None, priimek=None):
        if geslo2 is not None:
            if geslo != geslo2:
                nastavi_sporocilo("Gesli se ne ujemata!")
                res = None
            else:
                zgostitev = nastavi_geslo(geslo)
                try:
                    with baza:
                        cur.execute("""
                            INSERT INTO oseba (emso, ime, priimek, naslov, posta_id, up_ime, geslo)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (emso, ime, priimek, 'Doma', 1000, up_ime, zgostitev))
                    res = emso, ime, priimek, zgostitev, 0
                    response.set_cookie("uporabnik", emso, path="/", secret=SKRIVNOST)
                except Exception as ex:
                    print(ex)
                    nastavi_sporocilo("Registracija ni uspela!")
                    res = None
        elif up_ime is None:
            cur.execute("""
                SELECT emso, ime, priimek, geslo, admin FROM oseba
                WHERE emso = ?
            """, (emso, ))
            res = cur.fetchone()
        else:
            cur.execute("""
                SELECT emso, ime, priimek, geslo, admin FROM oseba
                WHERE up_ime = ?
            """, (up_ime, ))
            res = cur.fetchone()
            ok = False
            if res is not None:
                emso, ime, priimek, zgostitev, admin = res
                if preveri_geslo(geslo, zgostitev):
                    ok = True
                    response.set_cookie("uporabnik", emso, path="/", secret=SKRIVNOST)
            if not ok:
                nastavi_sporocilo("Prijava ni uspešna!")
                self.odjava()
                res = None
        if res is None:
            res = (None, None, None, None, 0)
        self.emso, self.ime, self.priimek, _, self.admin = res

    def odjava(self):
        response.delete_cookie("uporabnik", path="/")

    def template(self, *largs, **kwargs):
        """
        Izpis predloge s podajanjem funkcij url in nastavi_sporocilo.
        """
        return bottle.template(*largs, **kwargs, uporabnik=self,
                               url=bottle.url, sporocilo=nastavi_sporocilo)
    
    def preveri(self, emso):
        if self.emso != emso:
            abort(401, "Dostop prepovedan!")


    @staticmethod
    def admin(fun):
        @wraps(fun)
        def decorator(uporabnik, *largs, **kwargs):
            if not uporabnik.admin:
                abort(401, "Dostop prepovedan!")
            return fun(uporabnik, *largs, **kwargs)
        return decorator

    @staticmethod
    def prijavljen(fun):
        @wraps(fun)
        def decorator(uporabnik, *largs, **kwargs):
            if not uporabnik.emso:
                redirect(url('prijava'))
            return fun(uporabnik, *largs, **kwargs)
        return decorator

    @staticmethod
    def odjavljen(fun):
        @wraps(fun)
        def decorator(uporabnik, *largs, **kwargs):
            if uporabnik.emso:
                redirect(url('index'))
            return fun(uporabnik, *largs, **kwargs)
        return decorator

def run(**kwargs):
    """
    Zagon spletnega strežnika s privzetimi nastavitvami.
    """
    kwargs.setdefault("host", SERVER_HOST)
    kwargs.setdefault("port", SERVER_PORT)
    kwargs.setdefault("reloader", RELOADER)
    return bottle.run(**kwargs)


def nastavi_sporocilo(sporocilo=None):
    """
    Nastavitev in prikaz sporočila z napako.
    """
    staro = request.get_cookie("sporocilo", secret=SKRIVNOST)
    if sporocilo is None:
        response.delete_cookie("sporocilo", path="/")
    else:
        response.set_cookie("sporocilo", sporocilo, path="/", secret=SKRIVNOST)
    return staro


@route("/static/<filename:path>", name="static")
def static(filename):
    """
    Prikaz statičnih datotek.
    """
    return static_file(filename, root=STATIC_ROOT)


# Povozimo razred za poti z zgoraj definiranim
bottle.Route = Route

# Povezava na bazo
baza = sqlite3.connect(BAZA)
baza.set_trace_callback(print) # izpis stavkov SQL v terminal (za razhroščevanje pri razvoju)
# zapoved upoštevanja omejitev FOREIGN KEY
cur = baza.cursor()
cur.execute("PRAGMA foreign_keys = ON;")
cur.close()
