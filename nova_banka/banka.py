from bottle import *
import sqlite3

# KONFIGURACIJA
baza_datoteka = 'banka.db'

# Odkomentiraj, če želiš sporočila o napakah
debug(True)  # za izpise pri razvoju


@get('/')
def index():
    return 'Začetna stran'



baza = sqlite3.connect(baza_datoteka, isolation_level=None)
baza.set_trace_callback(print) # izpis sql stavkov v terminal (za debugiranje pri razvoju)
# zapoved upoštevanja omejitev FOREIGN KEY
cur = baza.cursor()
cur.execute("PRAGMA foreign_keys = ON;")

# reloader=True nam olajša razvoj (ozveževanje sproti - razvoj)
run(host='localhost', port=8080, reloader=True)
