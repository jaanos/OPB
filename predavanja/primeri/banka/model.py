from auth import auth
from dataclasses import dataclass
from datetime import datetime
from orm import povezi, stolpec, Entiteta, Funkcija, sql, fields

@dataclass
class Kraj(Entiteta):
    """
    Kraj z lastnostmi:
    - posta: poštna številka (glavni ključ)
    - kraj: ime kraja
    """

    posta: int = stolpec(glavni_kljuc=True)
    kraj: str = stolpec(obvezen=True)


@dataclass
class Oseba(Entiteta):
    """
    Oseba z lastnostmi:
    - emso: EMŠO osebe (glavni ključ)
    - ime: ime osebe
    - priimek: priimek osebe
    - naslov: naslov osebe
    - kraj: kraj osebe
    """

    emso: str = stolpec(glavni_kljuc=True)
    ime: str = stolpec(obvezen=True)
    priimek: str = stolpec(obvezen=True)
    naslov: str = stolpec(obvezen=True)
    kraj: Kraj = stolpec(obvezen=True)

    @classmethod
    def _stolpci(cls):
        """
        Vrni zaporedje stolpcev za branje iz baze.
        """
        yield from (sql.Identifier(stolpec.name) for stolpec in fields(cls)
                    if stolpec.name != 'kraj')
        kraj = sql.Identifier(Kraj.tabela())
        yield from (sql.SQL("{kraj}.{stolpec}").format(
                        kraj=kraj,
                        stolpec=sql.Identifier(stolpec.name)
                    )
                    for stolpec in fields(Kraj))

    @classmethod
    def _tabela(cls):
        """
        Vrni izraz za tabelo za branje iz baze.
        """
        return sql.SQL("""
            {tabela} JOIN {kraj} ON {tabela}.kraj = {kraj}.posta
        """).format(
            tabela=sql.Identifier(cls.tabela()),
            kraj=sql.Identifier(Kraj.tabela())
        )

    @classmethod
    def _objekt(cls, vrstica):
        """
        Vrni objekt po branju iz baze.
        """
        *vrstica, posta, kraj = vrstica
        return cls.iz_baze(*vrstica, Kraj.iz_baze(posta, kraj))


@dataclass
class Racun(Entiteta):
    """
    Račun z lastnostmi:
    - stevilka: številka računa (glavni ključ)
    - lastnik: lastnik računa
    """

    stevilka: int = stolpec(glavni_kljuc=True, stevec=True)
    lastnik: Oseba = stolpec(obvezen=True)

    @classmethod
    def _stolpci(cls):
        """
        Vrni zaporedje stolpcev za branje iz baze.
        """
        yield from super()._stolpci()
        yield from (sql.Identifier(stolpec) for stolpec in ('ime', 'priimek'))

    @classmethod
    def _tabela(cls):
        """
        Vrni izraz za tabelo za branje iz baze.
        """
        return sql.SQL("""
            {tabela} JOIN {oseba} ON {tabela}.lastnik = {oseba}.emso
        """).format(
            tabela=sql.Identifier(cls.tabela()),
            oseba=sql.Identifier(Oseba.tabela())
        )

    @classmethod
    def _objekt(cls, vrstica):
        """
        Vrni objekt po branju iz baze.
        """
        racun, lastnik, ime, priimek = vrstica
        return cls.iz_baze(racun, Oseba.iz_baze(lastnik, ime, priimek))

@dataclass
class Transakcija(Entiteta):
    """
    Transakcija z lastnostmi:
    - id: ID transakcije (glavni ključ)
    - racun: račun transakcije
    - znesek: nakazani znesek
    - cas: čas transakcije
    - opis: opis transakcije
    """

    id: int = stolpec(glavni_kljuc=True, stevec=True)
    racun: Racun = stolpec(obvezen=True)
    znesek: int = stolpec(obvezen=True)
    cas: datetime = stolpec(privzeto=Funkcija("NOW()"), obvezen=True)
    opis: str = stolpec()


ENTITETE = (Kraj, Oseba, Racun, Transakcija)


def ustvari_tabele(izbrisi=False, ce_ne_obstajajo=False):
    """
    Ustvari tabele v bazi.
    """
    with conn.transaction():
        if izbrisi:
            izbrisi_tabele(ce_ne_obstajajo)
        for entiteta in ENTITETE:
            entiteta.ustvari_tabelo(ce_ne_obstaja=ce_ne_obstajajo)


def izbrisi_tabele(ce_obstajajo=False):
    """
    Izbriši tabele iz baze.
    """
    with conn.transaction():
        for entiteta in reversed(ENTITETE):
            entiteta.izbrisi_tabelo(ce_obstajajo)


def uvozi_podatke():
    """
    Uvozi podatke v bazo.
    """
    with conn.transaction():
        for entiteta in ENTITETE:
            entiteta.uvozi_podatke()


def vzpostavi_povezavo(**kwargs):
    """
    Vzpostavi povezavo z bazo in jo inicializiraj.
    """
    global conn
    conn = povezi(**auth, **kwargs)
    ustvari_tabele(ce_ne_obstajajo=True)
    return conn
