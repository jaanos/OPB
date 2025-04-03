from dataclasses import field, fields
from datetime import datetime
from psycopg import connect, sql, errors
import csv


TIPI = {
    int: "INTEGER",
    str: "TEXT",
    datetime: "TIMESTAMP(0)"
}


LASTNOSTI = {
    "glavni_kljuc": "PRIMARY KEY",
    "obvezen": "NOT NULL",
    "enolicen": "UNIQUE"
}


def povezi(*largs, **kwargs):
    """
    Vzpostavi povezavo z bazo.
    """
    global conn
    conn = connect(*largs, **kwargs, autocommit=True)
    return conn


def stolpec(privzeto=None, glavni_kljuc=False, stevec=False, obvezen=False,
            enolicen=False):
    return field(default=privzeto,
                 metadata=dict(glavni_kljuc=glavni_kljuc, stevec=stevec,
                               obvezen=obvezen, enolicen=enolicen))


def tip(stolpec):
    t = stolpec.type
    while issubclass(t, Entiteta):
        t = t.glavni_kljuc().type
    return TIPI[t]


class Funkcija:
    def __init__(self, niz):
        self.niz = sql.SQL(niz)


class Entiteta:
    @classmethod
    def ustvari_tabelo(cls, pobrisi=False, ce_ne_obstaja=False):
        with conn.transaction():
            if pobrisi:
                cls.izbrisi_tabelo(ce_ne_obstaja)
            with conn.cursor() as cur:
                niz = sql.SQL("""
                    CREATE TABLE {ce_ne_obstaja} {tabela} ({stolpci});
                """).format(
                    ce_ne_obstaja=sql.SQL("IF NOT EXISTS" if ce_ne_obstaja else ""),
                    tabela=sql.Identifier(cls.tabela()),
                    stolpci=sql.SQL(", ").join(
                        sql.SQL("{ime} {tip} {lastnosti} {privzeto} {referenca}").format(
                            ime=sql.Identifier(stolpec.name),
                            tip=sql.SQL("SERIAL" if stolpec.metadata["stevec"] else tip(stolpec)),
                            lastnosti=sql.SQL(" ").join(
                                sql.SQL(niz) for lastnost, niz in LASTNOSTI.items()
                                if stolpec.metadata[lastnost]
                            ),
                            privzeto=sql.SQL("DEFAULT {vrednost}").format(
                                vrednost=stolpec.default.niz if isinstance(stolpec.default, Funkcija)
                                    else sql.Literal(stolpec.default)
                            ) if stolpec.default else sql.SQL(""),
                            referenca=sql.SQL("REFERENCES {tab}({st})").format(
                                tab=sql.Identifier(stolpec.type.tabela()),
                                st=sql.Identifier(stolpec.type.glavni_kljuc().name)
                            ) if issubclass(stolpec.type, Entiteta) else sql.SQL("")
                        )
                        for stolpec in fields(cls)
                    ))
                cur.execute(niz)

    @classmethod
    def izbrisi_tabelo(cls, ce_obstaja=False):
        with conn.transaction():
            with conn.cursor() as cur:
                cur.execute(sql.SQL("DROP TABLE {ce_obstaja} {tabela};").format(
                    ce_obstaja=sql.SQL("IF EXISTS" if ce_obstaja else ""),
                    tabela=sql.Identifier(cls.tabela())
                ))

    @classmethod
    def tabela(cls):
        if not hasattr(cls, "TABELA"):
            cls.TABELA = cls.__name__.lower()
        return cls.TABELA

    @classmethod
    def glavni_kljuc(cls):
        if not hasattr(cls, "GLAVNI_KLJUC"):
            cls.GLAVNI_KLJUC = next(stolpec for stolpec in fields(cls) if stolpec.metadata["glavni_kljuc"])
        return cls.GLAVNI_KLJUC

    @classmethod
    def uvozi_podatke(cls):
        with open(f"podatki/{cls.tabela()}.csv"):
            rd = csv.reader(f)
            stolpci = next(rd)
            for vrstica in rd:
                # vstavi podatke v bazo
                pass
