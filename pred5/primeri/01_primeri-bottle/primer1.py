# -*- encoding: utf-8 -*-

# Osnovni primer uporabe bottle, skopirano s spletnih strani

from bottle import route, run

@route('/')
def index():
    return 'ŽIVJO world!'

# Če dopišemo reloader=True, se bo sam restartal vsakič, ko spremenimo datoteko
run(host='localhost', port=8080, reloader=True)
