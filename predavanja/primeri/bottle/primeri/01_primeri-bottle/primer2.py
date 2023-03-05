#!/usr/bin/python
# -*- encoding: utf-8 -*-

# Drugi primer: kako serviramo različne naslove

from bottle import route, run, debug, abort

# Tole nastavimo, da bomo videli sporočila o napakah
debug(True)

@route('/')
def index():
    return 'To je glavni dokument.'

@route('/banana/')
def banana():
    return 'Tu serviramo banane.'

@route('/hello/<name>/')
def hello(name):
    return "Hello {0}".format(name)

@route('/vsota/<a>/<b>/')
def hello(a, b):
    # Pozor, a in b sta niza, pretvorimo ju v int
    try:
        a = int(a) # Sproži izjemo ValueError, če niz a ne predstavlja celega števila
        b = int(b) # Sproži izjemo ValueError, če niz b ne predstavlja celega števila
        return "Vsota števil {0} in {1} je {2}.".format(a,b,a+b)
    except ValueError:
        # Uporabnik je vpisal čudne podatke, javimo napako
        abort(402, 'Napačni podatki (pričakovali smo cela števila), plačaj!')


# Če dopišemo reloader=True, se bo sam restartal vsakič, ko spremenimo datoteko
run(host='localhost', port=8081, reloader=True)
