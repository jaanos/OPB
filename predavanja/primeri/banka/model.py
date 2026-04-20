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


@dataclass
class Oseba:
    emso: str
    ime: str
    priimek: str
    naslov: str
    kraj: Kraj

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
                        kraj INTEGER NOT NULL REFERENCES kraj(posta)
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

@dataclass
class Racun:
    stevilka: int
    lastnik: Oseba

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


@dataclass
class Transakcija:
    id: int
    racun: Racun
    znesek: int
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
