#!/usr/bin/python3
# -*- encoding: utf-8 -*-

# Osnovni primer uporabe bottle, skopirano s spletnih strani

from bottle import *
from bottlesession import session
import os

@get('/')
def index():
    response.content_type = "text/html; charset=UTF-8"
    sess = session()
    try:
        ime = sess.read("ime")
        spol = sess.read("spol")
        pozdrav = "Pozdravljen%s %s!" % ("a" if spol == "zenska" else "", ime)
    except:
        ime = ""
        spol = ""
        pozdrav = "Tebe pa ne poznam!"
    moski = "checked" if spol == "moski" else ""
    zenska = "checked" if spol == "zenska" else ""
    sess.close()
    return template("index.html", pozdrav=pozdrav, ime=ime, moski=moski, zenska=zenska)

@post('/')
def post():
    response.content_type = "text/html; charset=UTF-8"
    sess = session()
    sess.set("ime", request.POST.ime) # request.POST["ime"] ne deluje pravilno
    sess.set("spol", request.POST.spol) # s šumniki v Python3!
    sess.close()
    redirect("/")

# Če dopišemo reloader=True, se bo sam restartal vsakič, ko spremenimo datoteko
run(host='localhost', port=8080, reloader=True)
