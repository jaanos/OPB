import bcrypt
import csv
from psycopg import connect, sql, errors
from auth import auth
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Kraj:
    posta: int
    kraj: str

    def __str__(self):
        return f"{self.posta} {self.kraj}"

    @classmethod
    def ustvari_tabelo(cls, pobrisi=False, ce_ne_obstaja=False):
        with conn.transaction():
            if pobrisi:
                cls.izbrisi_tabelo(ce_ne_obstaja)
            with conn.cursor() as cur:
                cur.execute(sql.SQL(
                    """
                    CREATE TABLE {ce_ne_obstaja} kraj (
                        posta INTEGER PRIMARY KEY,
                        kraj TEXT NOT NULL
                    );
                    """).format(
                        ce_ne_obstaja=sql.SQL("IF NOT EXISTS" if ce_ne_obstaja else "")
                    ))

    @classmethod
    def izbrisi_tabelo(cls, ce_obstaja=False):
        with conn.transaction():
            with conn.cursor() as cur:
                cur.execute(sql.SQL(
                    """
                    DROP TABLE {ce_obstaja} kraj;
                    """).format(
                        ce_obstaja=sql.SQL("IF EXISTS" if ce_obstaja else "")
                    ))

    @classmethod
    def uvozi_podatke(cls):
        with conn.transaction():
            with conn.cursor() as cur:
                with open('podatki/kraj.csv') as f:
                    rd = csv.reader(f)
                    stolpci = next(rd)
                    for vrstica in rd:
                        podatki = dict(zip(stolpci, vrstica))
                        cur.execute(
                            """
                            INSERT INTO kraj (posta, kraj)
                            VALUES (%(posta)s, %(kraj)s)
                            """, podatki
                        )

    @classmethod
    def z_id(cls, id):
        with conn.transaction():
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT posta, kraj FROM kraj
                    WHERE posta = %s
                    """, (id, )
                )
                vrstica = cur.fetchone()
                if vrstica is None:
                    raise ValueError(f"Kraj s pošto {id} ne obstaja!")
                return Kraj(*vrstica)

    @classmethod
    def seznam(cls):
        with conn.transaction():
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT posta, kraj FROM kraj
                    ORDER BY posta
                    """
                )
                for vrstica in cur:
                    yield Kraj(*vrstica)

    def vstavi(self):
        with conn.transaction():
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO kraj (posta, kraj)
                    VALUES (%(posta)s, %(kraj)s)
                    """, self.kot_slovar()
                )

    def posodobi(self):
        with conn.transaction():
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE kraj SET kraj = %(kraj)s
                    WHERE posta = %(posta)s
                    """, self.kot_slovar()
                )

    def izbrisi(self):
        with conn.transaction():
            with conn.cursor() as cur:
                cur.execute(
                    """
                    DELETE FROM kraj
                    WHERE posta = %s
                    """, (self.posta, )
                )

    def kot_slovar(self):
        return dict(posta=self.posta, kraj=self.kraj)

@dataclass
class Oseba:
    emso: str
    ime: str
    priimek: str
    naslov: str = None
    kraj: Kraj = None
    uporabnisko_ime: str = None
    geslo: bytes = None
    admin: bool = False

    @classmethod
    def ustvari_tabelo(cls, pobrisi=False, ce_ne_obstaja=False):
        with conn.transaction():
            if pobrisi:
                cls.izbrisi_tabelo(ce_ne_obstaja)
            with conn.cursor() as cur:
                cur.execute(sql.SQL(
                    """
                    CREATE TABLE {ce_ne_obstaja} oseba (
                        emso TEXT PRIMARY KEY,
                        ime TEXT NOT NULL,
                        priimek TEXT NOT NULL,
                        naslov TEXT NOT NULL,
                        kraj INTEGER NOT NULL REFERENCES kraj(posta),
                        uporabnisko_ime TEXT NOT NULL UNIQUE,
                        geslo BYTEA,
                        admin BOOLEAN NOT NULL DEFAULT (FALSE)
                    );
                    """).format(
                        ce_ne_obstaja=sql.SQL("IF NOT EXISTS" if ce_ne_obstaja else "")
                    ))

    @classmethod
    def izbrisi_tabelo(cls, ce_obstaja=False):
        with conn.transaction():
            with conn.cursor() as cur:
                cur.execute(sql.SQL(
                    """
                    DROP TABLE {ce_obstaja} oseba;
                    """).format(
                        ce_obstaja=sql.SQL("IF EXISTS" if ce_obstaja else "")
                    ))

    @classmethod
    def uvozi_podatke(cls):
        with conn.transaction():
            with conn.cursor() as cur:
                with open('podatki/oseba.csv') as f:
                    rd = csv.reader(f)
                    stolpci = next(rd)
                    for vrstica in rd:
                        podatki = dict(zip(stolpci, vrstica))
                        if podatki['geslo']:
                            podatki['geslo'] = Oseba._nastavi_geslo(podatki['geslo'])
                        else:
                            podatki['geslo'] = None
                        podatki['admin'] = (podatki['emso'] == '1')
                        cur.execute(
                            """
                            INSERT INTO oseba (emso, ime, priimek, naslov, kraj, uporabnisko_ime, geslo, admin)
                            VALUES (%(emso)s, %(ime)s, %(priimek)s, %(naslov)s, %(kraj)s,
                                    %(uporabnisko_ime)s, %(geslo)s, %(admin)s)
                            """, podatki
                        )

    @classmethod
    def z_id(cls, id):
        with conn.transaction():
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT emso, ime, priimek, naslov, kraj.posta, kraj.kraj, uporabnisko_ime, admin FROM oseba
                    JOIN kraj ON oseba.kraj = posta
                    WHERE emso = %s
                    """, (id, )
                )
                vrstica = cur.fetchone()
                if vrstica is None:
                    raise ValueError(f"Uporabnik z EMŠOm {id} ne obstaja!")
                *podatki, posta, kraj, uporabnisko_ime, admin = vrstica
                return Oseba(*podatki, Kraj(posta, kraj), uporabnisko_ime, admin=admin)

    @classmethod
    def prijavi(cls, uporabnisko_ime, geslo):
        with conn.transaction():
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT emso, ime, priimek, naslov, kraj.posta, kraj.kraj, uporabnisko_ime, geslo, admin FROM oseba
                    JOIN kraj ON oseba.kraj = posta
                    WHERE uporabnisko_ime = %s
                    """, (uporabnisko_ime, )
                )
                vrstica = cur.fetchone()
                if vrstica is None:
                    raise ValueError(f"Uporabnik z uporabniškim imenom {uporabnisko_ime} ne obstaja!")
                *podatki, posta, kraj, uporabnisko_ime, zgostitev, admin = vrstica
                if not Oseba._preveri_geslo(geslo, zgostitev):
                    raise ValueError(f"Geslo za uporabnika z uporabniškim imenom {uporabnisko_ime} ni pravilno!")
                return Oseba(*podatki, Kraj(posta, kraj), uporabnisko_ime, admin=admin)

    @classmethod
    def seznam(cls):
        with conn.transaction():
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT emso, ime, priimek, naslov, kraj.posta, kraj.kraj, uporabnisko_ime, admin FROM oseba
                    JOIN kraj ON oseba.kraj = posta
                    ORDER BY priimek, ime
                    """
                )
                for *podatki, posta, kraj, uporabnisko_ime, admin in cur:
                    yield Oseba(*podatki, Kraj(posta, kraj), uporabnisko_ime, admin=admin)

    def racuni(self):
        with conn.transaction():
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT stevilka FROM racun
                    WHERE lastnik = %s
                    ORDER BY stevilka
                    """, (self.emso, )
                )
                for stevilka, in cur:
                    yield Racun(stevilka, self)

    def dodaj_racun(self):
        racun = Racun(lastnik=self)
        racun.vstavi()
        return racun

    def vstavi(self):
        with conn.transaction():
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO oseba (emso, ime, priimek, naslov, kraj, uporabnisko_ime, geslo, admin)
                    VALUES (%(emso)s, %(ime)s, %(priimek)s, %(naslov)s, %(kraj)s,
                            %(uporabnisko_ime)s, %(geslo)s, %(admin)s)
                    """, self.kot_slovar()
                )
                self.geslo = None

    def posodobi(self):
        with conn.transaction():
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE oseba SET ime = %(ime)s, priimek = %(priimek)s, naslov = %(naslov)s,
                                     kraj = %(kraj)s, uporabnisko_ime = %(uporabnisko_ime)s, admin = %(admin)s
                    WHERE emso = %(emso)s
                    """, self.kot_slovar()
                )

    def izbrisi(self):
        with conn.transaction():
            with conn.cursor() as cur:
                cur.execute(
                    """
                    DELETE FROM oseba
                    WHERE emso = %s
                    """, (self.emso, )
                )

    def kot_slovar(self):
        if isinstance(self.kraj, Kraj):
            kraj = self.kraj.posta
        else:
            kraj = self.kraj
        if self.geslo is None:
            geslo = None
        else:
            geslo = Oseba._nastavi_geslo(self.geslo)
        return dict(emso=self.emso, ime=self.ime, priimek=self.priimek, naslov=self.naslov, kraj=kraj,
                    uporabnisko_ime=self.uporabnisko_ime, geslo=geslo, admin=self.admin)

    @staticmethod
    def _nastavi_geslo(geslo):
        """
        Vrni zgostitev podanega gesla.
        """
        geslo = geslo.encode("utf-8")
        sol = bcrypt.gensalt()
        return bcrypt.hashpw(geslo, sol)

    @staticmethod
    def _preveri_geslo(geslo, zgostitev):
        """
        Preveri podano geslo glede na podano zgostitev.
        """
        geslo = geslo.encode("utf-8")
        return bcrypt.checkpw(geslo, zgostitev)


@dataclass
class Racun:
    stevilka: int = None
    lastnik: Oseba = None

    @classmethod
    def ustvari_tabelo(cls, pobrisi=False, ce_ne_obstaja=False):
        with conn.transaction():
            if pobrisi:
                cls.izbrisi_tabelo(ce_ne_obstaja)
            with conn.cursor() as cur:
                cur.execute(sql.SQL(
                    """
                    CREATE TABLE {ce_ne_obstaja} racun (
                        stevilka SERIAL PRIMARY KEY,
                        lastnik TEXT NOT NULL REFERENCES oseba(emso)
                    );
                    """).format(
                        ce_ne_obstaja=sql.SQL("IF NOT EXISTS" if ce_ne_obstaja else "")
                    ))

    @classmethod
    def izbrisi_tabelo(cls, ce_obstaja=False):
        with conn.transaction():
            with conn.cursor() as cur:
                cur.execute(sql.SQL(
                    """
                    DROP TABLE {ce_obstaja} racun;
                    """).format(
                        ce_obstaja=sql.SQL("IF EXISTS" if ce_obstaja else "")
                    ))

    @classmethod
    def uvozi_podatke(cls):
        with conn.transaction():
            with conn.cursor() as cur:
                with open('podatki/racun.csv') as f:
                    rd = csv.reader(f)
                    stolpci = next(rd)
                    for vrstica in rd:
                        podatki = dict(zip(stolpci, vrstica))
                        cur.execute(
                            """
                            INSERT INTO racun (stevilka, lastnik)
                            VALUES (%(stevilka)s, %(lastnik)s)
                            """, podatki
                        )
                cur.execute(
                    """
                    SELECT MAX(stevilka) FROM racun
                    """
                )
                stevec, = cur.fetchone()
                cur.execute(sql.SQL(
                    """
                    ALTER SEQUENCE racun_stevilka_seq RESTART WITH {vrednost}
                    """
                ).format(vrednost=sql.Literal(stevec + 1)))

    @classmethod
    def z_id(cls, id):
        with conn.transaction():
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT stevilka, emso, ime, priimek, naslov, kraj.posta, kraj.kraj, uporabnisko_ime, admin FROM racun
                    JOIN oseba ON lastnik = emso
                    JOIN kraj ON oseba.kraj = posta
                    WHERE stevilka = %s
                    """, (id, )
                )
                vrstica = cur.fetchone()
                if vrstica is None:
                    raise ValueError(f"Račun s številko {id} ne obstaja!")
                stevilka, *podatki, posta, kraj, uporabnisko_ime, admin = vrstica
                return Racun(stevilka, Oseba(*podatki, Kraj(posta, kraj), uporabnisko_ime, admin=admin))

    @classmethod
    def seznam(cls):
        with conn.transaction():
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT stevilka, emso, ime, priimek FROM racun
                    JOIN oseba ON lastnik = emso
                    ORDER BY stevilka
                    """
                )
                for stevilka, *podatki in cur:
                    yield Racun(stevilka, Oseba(*podatki))

    def transakcije(self):
        with conn.transaction():
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, znesek, cas, opis FROM transakcija
                    WHERE racun = %s
                    ORDER BY cas DESC
                    """, (self.stevilka, )
                )
                for id, *podatki in cur:
                    yield Transakcija(id, self, *podatki)

    def vstavi(self):
        assert self.stevilka is None, f"Račun že ima dodeljeno številko {self.stevilka}!"
        with conn.transaction():
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO racun (lastnik)
                    VALUES (%(lastnik)s)
                    RETURNING stevilka
                    """, self.kot_slovar()
                )
                self.stevilka, = cur.fetchone()

    def posodobi(self):
        assert self.stevilka is not None, "Račun še nima dodeljene številke!"
        with conn.transaction():
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE racun SET lastnik = %(lastnik)s
                    WHERE stevilka = %(stevilka)s
                    """, self.kot_slovar()
                )

    def izbrisi(self):
        assert self.stevilka is not None, "Račun še nima dodeljene številke!"
        with conn.transaction():
            with conn.cursor() as cur:
                cur.execute(
                    """
                    DELETE FROM racun
                    WHERE stevilka = %s
                    """, (self.stevilka, )
                )

    def kot_slovar(self):
        if isinstance(self.lastnik, Oseba):
            lastnik = self.lastnik.emso
        else:
            lastnik = self.lastnik
        return dict(stevilka=self.stevilka, lastnik=lastnik)


@dataclass
class Transakcija:
    id: int = None
    racun: Racun = None
    znesek: int = None
    cas: datetime = None
    opis: str = None

    @classmethod
    def ustvari_tabelo(cls, pobrisi=False, ce_ne_obstaja=False):
        with conn.transaction():
            if pobrisi:
                cls.izbrisi_tabelo(ce_ne_obstaja)
            with conn.cursor() as cur:
                cur.execute(sql.SQL(
                    """
                    CREATE TABLE {ce_ne_obstaja} transakcija (
                        id SERIAL PRIMARY KEY,
                        racun INTEGER NOT NULL REFERENCES racun(stevilka),
                        znesek INTEGER NOT NULL,
                        cas TIMESTAMP(0) NOT NULL DEFAULT (NOW()),
                        opis TEXT
                    );
                    """).format(
                        ce_ne_obstaja=sql.SQL("IF NOT EXISTS" if ce_ne_obstaja else "")
                    ))

    @classmethod
    def izbrisi_tabelo(cls, ce_obstaja=False):
        with conn.transaction():
            with conn.cursor() as cur:
                cur.execute(sql.SQL(
                    """
                    DROP TABLE {ce_obstaja} transakcija;
                    """).format(
                        ce_obstaja=sql.SQL("IF EXISTS" if ce_obstaja else "")
                    ))

    @classmethod
    def uvozi_podatke(cls):
        with conn.transaction():
            with conn.cursor() as cur:
                with open('podatki/transakcija.csv') as f:
                    rd = csv.reader(f)
                    stolpci = next(rd)
                    for vrstica in rd:
                        podatki = dict(zip(stolpci, vrstica))
                        cur.execute(
                            """
                            INSERT INTO transakcija (id, racun, znesek, cas, opis)
                            VALUES (%(id)s, %(racun)s, %(znesek)s, %(cas)s, %(opis)s)
                            """, podatki
                        )
                cur.execute(
                    """
                    SELECT MAX(id) FROM transakcija
                    """
                )
                stevec, = cur.fetchone()
                cur.execute(sql.SQL(
                    """
                    ALTER SEQUENCE transakcija_id_seq RESTART WITH {vrednost}
                    """
                ).format(vrednost=sql.Literal(stevec + 1)))

    @classmethod
    def z_id(cls, id):
        with conn.transaction():
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, racun, znesek, cas, opis, emso, ime, priimek, naslov,
                           kraj.posta, kraj.kraj, uporabnisko_ime, admin FROM transakcija
                    JOIN racun ON racun = stevilka
                    JOIN oseba ON lastnik = emso
                    JOIN kraj ON oseba.kraj = posta
                    WHERE id = %s
                    """, (id, )
                )
                vrstica = cur.fetchone()
                if vrstica is None:
                    raise ValueError(f"Transakcija z ID-jem {id} ne obstaja!")
                id, racun, znesek, cas, opis, *podatki, posta, kraj, uporabnisko_ime, admin = vrstica
                return Transakcija(id, Racun(racun, Oseba(*podatki, Kraj(posta, kraj), uporabnisko_ime, admin=admin)),
                                   znesek, cas, opis)

    @classmethod
    def seznam(cls):
        with conn.transaction():
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, racun, znesek, cas, opis FROM transakcija
                    ORDER BY cas DESC
                    """
                )
                for podatki in cur:
                    yield Transakcija(*podatki)

    def vstavi(self):
        assert self.id is None, f"Transakcija že ima dodeljen ID {self.id}!"
        assert self.cas is None, f"Transakcija že ima dodeljen čas {self.cas}!"
        with conn.transaction():
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO transakcija (racun, znesek, opis)
                    VALUES (%(racun)s, %(znesek)s, %(opis)s)
                    RETURNING id, cas
                    """, self.kot_slovar()
                )
                self.id, self.cas = cur.fetchone()

    def posodobi(self):
        assert self.id is not None, "Transakcija še nima dodeljenega ID-ja!"
        with conn.transaction():
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE transakcija SET racun = %(racun)s, znesek = %(znesek)s, cas = %(cas)s, opis = %(opis)s
                    WHERE id = %(id)s
                    """, self.kot_slovar()
                )

    def izbrisi(self):
        assert self.id is not None, "Transakcija še nima dodeljenega ID-ja!"
        with conn.transaction():
            with conn.cursor() as cur:
                cur.execute(
                    """
                    DELETE FROM transakcija
                    WHERE id = %s
                    """, (self.id, )
                )

    def kot_slovar(self):
        if isinstance(self.racun, Racun):
            racun = self.racun.stevilka
        else:
            racun = self.racun
        return dict(id=self.id, racun=racun, znesek=self.znesek, cas=self.cas, opis=self.opis)


RAZREDI = [Kraj, Oseba, Racun, Transakcija]


def ustvari_tabele(pobrisi=False, ce_ne_obstaja=False):
    with conn.transaction():
        if pobrisi:
            for cls in reversed(RAZREDI):
                cls.izbrisi_tabelo(ce_ne_obstaja)
        for cls in RAZREDI:
            cls.ustvari_tabelo(ce_ne_obstaja=ce_ne_obstaja)


def vzpostavi_povezavo(**kwargs):
    global conn
    conn = connect(**auth, **kwargs)
    return conn
