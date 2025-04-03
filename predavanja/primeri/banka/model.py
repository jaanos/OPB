from auth import auth
from dataclasses import dataclass
from datetime import datetime
from orm import povezi, stolpec, Entiteta, Funkcija

@dataclass
class Kraj(Entiteta):
    posta: int = stolpec(glavni_kljuc=True)
    kraj: str = stolpec(obvezen=True)


@dataclass
class Oseba(Entiteta):
    emso: str = stolpec(glavni_kljuc=True)
    ime: str = stolpec(obvezen=True)
    priimek: str = stolpec(obvezen=True)
    naslov: str = stolpec(obvezen=True)
    kraj: Kraj = stolpec(obvezen=True)


@dataclass
class Racun(Entiteta):
    stevilka: int = stolpec(glavni_kljuc=True, stevec=True)
    lastnik: Oseba = stolpec(obvezen=True)


@dataclass
class Transakcija(Entiteta):
    id: int = stolpec(glavni_kljuc=True, stevec=True)
    racun: Racun = stolpec(obvezen=True)
    znesek: int = stolpec(obvezen=True)
    cas: datetime = stolpec(privzeto=Funkcija("NOW()"), obvezen=True)
    opis: str = stolpec()


def ustvari_tabele(izbrisi=False, ce_ne_obstajajo=False):
    with conn.transaction():
        if izbrisi:
            izbrisi_tabele(ce_ne_obstajajo)
        for entiteta in ENTITETE:
            entiteta.ustvari_tabelo(ce_ne_obstaja=ce_ne_obstajajo)


def izbrisi_tabele(ce_obstajajo=False):
    with conn.transaction():
        for entiteta in reversed(ENTITETE):
            entiteta.izbrisi_tabelo(ce_obstajajo)


ENTITETE = (Kraj, Oseba, Racun, Transakcija)
conn = povezi(**auth)
ustvari_tabele(ce_ne_obstajajo=True)
