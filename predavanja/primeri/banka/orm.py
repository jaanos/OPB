from dataclasses import field, fields
from datetime import datetime
from psycopg import connect, sql, errors
import csv


PRAZNO = sql.SQL("")
PRESLEDEK = sql.SQL(" ")
VEJICA = sql.SQL(", ")

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
    """
    Vrni polje, ki opisuje stolpec v tabeli.
    """
    return field(default=privzeto,
                 metadata=dict(glavni_kljuc=glavni_kljuc, stevec=stevec,
                               obvezen=obvezen, enolicen=enolicen))


def tip(stolpec):
    """
    Vrni tip stolpca v tabeli.
    """
    t = stolpec.type
    while issubclass(t, Entiteta):
        t = t.glavni_kljuc().type
    return TIPI[t]


class Funkcija:
    """
    Razred za definicije funkcij v SQL.
    """
    def __init__(self, niz):
        self.niz = sql.SQL(niz)


class Entiteta:
    """
    Nadrazred za posamezne entitetne tipe.
    """

    def __post_init__(self):
        """
        Inicializiraj polje z ID-jem iz baze.
        """
        self.__dbid = None

    def __getitem__(self, kljuc):
        """
        Vrni vrednost v stolpcu v obliki, kot je zapisana v bazi.
        """
        vrednost = getattr(self, kljuc)
        if isinstance(vrednost, Entiteta):
            return vrednost[vrednost.glavni_kljuc().name]
        else:
            return vrednost

    def __nastavi_id(self):
        """
        Nastavi ID na glavni ključ.
        """
        self.__dbid = self[self.glavni_kljuc().name]

    @classmethod
    def ustvari_tabelo(cls, pobrisi=False, ce_ne_obstaja=False):
        """
        Ustvari tabelo v bazi.
        """
        with conn.transaction():
            if pobrisi:
                cls.izbrisi_tabelo(ce_ne_obstaja)
            with conn.cursor() as cur:
                cur.execute(sql.SQL("""
                    CREATE TABLE {ce_ne_obstaja} {tabela} ({stolpci});
                """).format(
                    ce_ne_obstaja=sql.SQL("IF NOT EXISTS"
                                          if ce_ne_obstaja else ""),
                    tabela=sql.Identifier(cls.tabela()),
                    stolpci=VEJICA.join(
                        sql.SQL("""
                            {ime} {tip} {lastnosti} {privzeto} {referenca}
                        """).format(
                            ime=sql.Identifier(stolpec.name),
                            tip=sql.SQL("SERIAL" if stolpec.metadata["stevec"]
                                        else tip(stolpec)),
                            lastnosti=PRESLEDEK.join(
                                sql.SQL(niz)
                                for lastnost, niz in LASTNOSTI.items()
                                if stolpec.metadata[lastnost]
                            ),
                            privzeto=sql.SQL("DEFAULT {vrednost}").format(
                                vrednost=stolpec.default.niz
                                    if isinstance(stolpec.default, Funkcija)
                                    else sql.Literal(stolpec.default)
                            ) if stolpec.default else PRAZNO,
                            referenca=sql.SQL("REFERENCES {tab}({st})").format(
                                tab=sql.Identifier(stolpec.type.tabela()),
                                st=sql.Identifier(stolpec.type.glavni_kljuc().name)
                            ) if issubclass(stolpec.type, Entiteta)
                            else PRAZNO
                        )
                        for stolpec in fields(cls)
                    )))

    @classmethod
    def izbrisi_tabelo(cls, ce_obstaja=False):
        """
        Izbriši tabelo iz baze.
        """
        with conn.transaction():
            with conn.cursor() as cur:
                cur.execute(sql.SQL("""
                    DROP TABLE {ce_obstaja} {tabela};
                """).format(
                    ce_obstaja=sql.SQL("IF EXISTS" if ce_obstaja else ""),
                    tabela=sql.Identifier(cls.tabela())
                ))

    @classmethod
    def tabela(cls):
        """
        Vrni ime tabele.
        """
        if not hasattr(cls, "TABELA"):
            cls.TABELA = cls.__name__.lower()
        return cls.TABELA

    @classmethod
    def glavni_kljuc(cls):
        """
        Vrni definicijo glavnega ključa.
        """
        if not hasattr(cls, "GLAVNI_KLJUC"):
            cls.GLAVNI_KLJUC = next(stolpec for stolpec in fields(cls)
                                    if stolpec.metadata["glavni_kljuc"])
        return cls.GLAVNI_KLJUC

    @classmethod
    def uvozi_podatke(cls):
        """
        Uvozi podatke v tabelo.
        """
        with open(f"podatki/{cls.tabela()}.csv") as f:
            rd = csv.reader(f)
            stolpci = next(rd)
            with conn.transaction():
                with conn.cursor() as cur:
                    cur.executemany(sql.SQL("""
                        INSERT INTO {tabela} ({stolpci}) VALUES ({podatki});
                    """).format(
                        tabela=sql.Identifier(cls.tabela()),
                        stolpci=VEJICA.join(
                            sql.Identifier(stolpec) for stolpec in stolpci
                        ),
                        podatki=VEJICA.join(
                            sql.Placeholder(stolpec) for stolpec in stolpci
                        )
                    ), ({stolpec: (podatek if podatek else None)
                         for stolpec, podatek in zip(stolpci, vrstica)}
                        for vrstica in rd))

    @classmethod
    def z_id(cls, id):
        """
        Vrni entiteto s podanim ID-jem.
        """
        with conn.cursor() as cur:
            cur.execute(sql.SQL("""
                SELECT {stolpci} FROM {tabela}
                WHERE {glavni_kljuc} = {id};
            """).format(
                stolpci=VEJICA.join(sql.Identifier(stolpec.name)
                                    for stolpec in fields(cls)),
                tabela=sql.Identifier(cls.tabela()),
                glavni_kljuc=sql.Identifier(cls.glavni_kljuc().name),
                id=sql.Literal(id)
            ))
            vrstica = cur.fetchone()
            if not vrstica:
                raise ValueError(f'{cls.__name__} z ID-jem {id} ne obstaja!')
            self = cls(*vrstica)
            self.__nastavi_id()
            return self

    def vstavi(self):
        """
        Vstavi entiteto v tabelo.
        """
        stolpci = []
        podatki = []
        generirani = []
        for stolpec in fields(self):
            vrednost = self[stolpec.name]
            if vrednost is not None:
                stolpci.append(stolpec.name)
                if isinstance(vrednost, Funkcija):
                    podatki.append(vrednost.niz)
                    generirani.append(stolpec.name)
                else:
                    podatki.append(sql.Literal(vrednost))
            elif stolpec.metadata["stevec"]:
                generirani.append(stolpec.name)
        with conn.transaction():
            with conn.cursor() as cur:
                cur.execute(sql.SQL("""
                    INSERT INTO {tabela} ({stolpci}) VALUES ({podatki})
                    {generirano};
                """).format(
                    tabela=sql.Identifier(self.tabela()),
                    stolpci=VEJICA.join(sql.Identifier(stolpec)
                                        for stolpec in stolpci),
                    podatki=VEJICA.join(podatki),
                    generirano=sql.SQL("RETURNING {generirani}").format(
                        generirani=VEJICA.join(sql.Identifier(stolpec)
                                               for stolpec in generirani)
                    ) if generirani else PRAZNO
                ))
                if generirani:
                    for kljuc, vrednost in zip(generirani, cur.fetchone()):
                        setattr(self, kljuc, vrednost)
                self.__nastavi_id()

    def posodobi(self):
        """
        Posodobi entiteto v bazi.
        """
        assert self.__dbid is not None, "Entiteta še ni v bazi!"
        with conn.transaction():
            with conn.cursor() as cur:
                cur.execute(sql.SQL("""
                    UPDATE {tabela} SET {vrednosti}
                    WHERE {glavni_kljuc} = {id};
                """).format(
                    tabela=sql.Identifier(self.tabela()),
                    vrednosti=VEJICA.join(
                        sql.SQL("""
                            {stolpec} = {vrednost}
                        """).format(
                            stolpec=sql.Identifier(stolpec.name),
                            vrednost=vrednost.niz
                                if isinstance(vrednost, Funkcija)
                                else sql.Literal(vrednost)
                        )
                        for stolpec in fields(self)
                        for vrednost in [self[stolpec.name]]
                    ),
                    glavni_kljuc=sql.Identifier(self.glavni_kljuc().name),
                    id=sql.Literal(self.__dbid)
                ))
                self.__nastavi_id()

    def izbrisi(self):
        """
        Izbriši entiteto iz baze.
        """
        assert self.__dbid is not None, "Entiteta še ni v bazi!"
        with conn.transaction():
            with conn.cursor() as cur:
                cur.execute(sql.SQL("""
                    DELETE FROM {tabela}
                    WHERE {glavni_kljuc} = {id};
                """).format(
                    tabela=sql.Identifier(self.tabela()),
                    glavni_kljuc=sql.Identifier(self.glavni_kljuc().name),
                    id=sql.Literal(self.__dbid)
                ))
                self.__dbid = None
