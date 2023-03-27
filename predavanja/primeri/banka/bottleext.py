import os
import bottle
import sqlite3
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
            try:
                cur = baza.cursor()
                return callback(cur, *largs, **kwargs)
            finally:
                cur.close()

        super().__init__(app, rule, method, decorator, name, plugins, skiplist, **config)


def template(*largs, **kwargs):
    """
    Izpis predloge s podajanjem funkcij url in nastavi_sporocilo.
    """
    return bottle.template(*largs, **kwargs, url=bottle.url, sporocilo=nastavi_sporocilo)


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
