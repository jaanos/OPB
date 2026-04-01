from dataclasses import field, fields
from datetime import datetime
from functools import wraps
from psycopg import connect, sql, errors
from types import MethodType
import csv


PRAZNO = sql.SQL("")
PRESLEDEK = sql.SQL(" ")
VEJICA = sql.SQL(", ")
STEVILO = 50

TIPI = {
    int: "INTEGER",
    str: "TEXT",
    bytes: "BYTEA",
    bool: "BOOLEAN",
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
            enolicen=False, skrit=False):
    """
    Vrni polje, ki opisuje stolpec v tabeli.
    """
    return field(default=privzeto,
                 metadata=dict(glavni_kljuc=glavni_kljuc, stevec=stevec,
                               obvezen=obvezen, enolicen=enolicen,
                               skrit=skrit))


def tip(stolpec):
    """
    Vrni tip stolpca v tabeli.
    """
    t = stolpec.type
    while issubclass(t, Entiteta):
        t = t.glavni_kljuc().type
    return TIPI[t]


class Rezultat:
    """
    Razred za rezultate poizvedb v seznamu.
    """
    def __init__(self, gen, stevilo, stran, skupaj):
        """
        Konstruktor rezultata.
        """
        self.gen = gen
        self.stevilo = stevilo
        self.stran = stran
        self.skupaj = skupaj
        if stevilo is None:
            self.dolzina = skupaj
        elif (stran + 1) * stevilo <= skupaj:
            self.dolzina = stevilo
        elif stran * stevilo >= skupaj:
            self.dolzina = 0
        else:
            self.dolzina = skupaj % stevilo

    def __iter__(self):
        """
        Iteriraj čez rezultat.
        """
        yield from self.gen

    def __len__(self):
        """
        Število vnosov v rezultatu.
        """
        return self.dolzina


class Seznam:
    """
    Razred za sezname z deljenjem na strani.
    """
    def __init__(self, fun=None, stevilo=STEVILO, stolpci=None, tabela=None,
                 join=None, pogoji=None, zdruzevanje=None, urejanje=None, podatki=()):
        """
        Konstruktor seznama.

        Možno ga je uporabiti kot dekorator.
        """
        self.fun = None
        self.stevilo = stevilo
        self.stolpci = stolpci
        self.tabela = tabela
        self.join = join
        self.pogoji = pogoji
        self.zdruzevanje = zdruzevanje
        self.urejanje = urejanje
        self.podatki = podatki
        self.objekt = None
        if fun:
            self(fun)

    def __call__(self, *largs, **kwargs):
        """
        Klic seznama za uporabo kot dekorator.

        Če je funkcija že nastavljena, jo kliče s podanimi parametri.
        """
        if self.fun:
            return self.fun(*largs, **kwargs)
        fun, = largs
        self.tip = type(fun)
        if isinstance(fun, (classmethod, staticmethod)):
            fun = fun.__func__
        @wraps(fun)
        def wrapper(*largs, stevilo=self.stevilo, stran=0, uredi=None, **kwargs):
            largs, kwargs = self.obdelaj_argumente(largs, kwargs)
            stolpci, tabela, join, pogoji, zdruzevanje, urejanje, podatki = \
                self.vrni_poizvedbo(*largs, uredi=uredi, **kwargs)
            def generator(podatki=podatki):
                with conn.transaction():
                    with conn.cursor() as cur:
                        cur.execute(sql.SQL("""
                            SELECT COUNT(*) FROM {tabela} {pogoji};
                        """).format(tabela=tabela, pogoji=pogoji), podatki)
                        skupaj, = cur.fetchone()
                        yield skupaj
                        if stevilo:
                            odmik = stran * stevilo
                            if isinstance(podatki, dict):
                                __stevilo = '__stevilo'
                                __odmik = '__odmik'
                                podatki = dict(**podatki, __stevilo=stevilo,
                                               __odmik=odmik)
                            else:
                                __stevilo = __odmik = ''
                                podatki = (*podatki, stevilo, odmik)
                            limit = sql.SQL(
                                "LIMIT {__stevilo} OFFSET {__odmik}"
                            ).format(
                                __stevilo=sql.Placeholder(__stevilo),
                                __odmik=sql.Placeholder(__odmik)
                            )
                        else:
                            limit = PRAZNO
                        cur.execute(sql.SQL("""
                            SELECT {stolpci} FROM {tabela} {join}
                            {pogoji} {zdruzevanje} {urejanje} {limit};
                        """).format(
                            stolpci=stolpci,
                            tabela=tabela,
                            join=join,
                            pogoji=pogoji,
                            zdruzevanje=zdruzevanje,
                            urejanje=urejanje,
                            limit=limit
                        ), podatki)
                        yield from fun(*largs, cur=cur, **kwargs)
            gen = generator()
            skupaj = next(gen)
            return Rezultat(gen, stevilo, stran, skupaj)
        self.fun = wrapper
        return self

    def __get__(self, instance, owner=None):
        """
        Vrni ustrezno metodo glede na način klicanja.
        """
        if self.objekt is None:
            self.objekt = owner
        if issubclass(self.tip, classmethod):
            return MethodType(self.fun, owner)
        elif issubclass(self.tip, staticmethod) or instance is None:
            return self.fun
        else:
            return MethodType(self.fun, instance)

    def obdelaj_argumente(self, largs, kwargs):
        """
        Obdelaj argumente za nadaljnje klice.

        Privzeto ne spremeni argumentov, lahko se nadomesti z metodo argumenti.
        """
        return (largs, kwargs)

    def sestavi_poizvedbo(self, *largs, **kwargs):
        """
        Vrni slovar s specifikacijo stolpcev, glavnega dela stavka SQL in
        podatkov. Manjkajoči ključi se nadomestijo s privzetimi vrednostmi.

        Privzeto vrača prazen slovar, lahko se nadomesti z metodo poizvedba.
        """
        return {}

    def vrni_poizvedbo(self, *largs, uredi=None, **kwargs):
        """
        Vrni trojico s specifikacijo stolpcev, glavnega dela stavka SQL in
        podatkov.
        """
        poizvedba = dict(stolpci=self.stolpci, tabela=self.tabela,
                         join=self.join, pogoji=self.pogoji,
                         zdruzevanje=self.zdruzevanje, urejanje=self.urejanje,
                         podatki=self.podatki, objekt=self.objekt)
        polja = tuple(poizvedba.keys())
        poizvedba.update(self.sestavi_poizvedbo(*largs, **kwargs))
        if uredi and any(stolpec.name == uredi
                         for stolpec in fields(poizvedba['objekt'])):
            poizvedba['urejanje'] = sql.SQL("""
                ORDER BY {uredi}
            """).format(uredi=sql.Identifier(uredi))
        return tuple(PRAZNO if poizvedba[k] is None else poizvedba[k]
                     for k in polja if k != 'objekt')

    def argumenti(self, fun):
        """
        Nastavi funkcijo za obdelavo argumentov.
        """
        self.obdelaj_argumente = fun
        return self

    def poizvedba(self, fun):
        """
        Nastavi funkcijo za sestavljanje poizvedbe.
        """
        self.sestavi_poizvedbo = fun
        return self


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

    def __init_subclass__(cls):
        """
        Inicializiraj prazen objekt.
        """
        cls.NULL = cls()
        cls.NULL.__post_init__()

    def __post_init__(self):
        """
        Inicializiraj polje z ID-jem iz baze.
        """
        self.__dbid = None

    def __bool__(self):
        """
        Vrni resničnostno vrednost za entiteto.
        """
        return self.__dbid is not None

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
    def iz_baze(cls, *largs, **kwargs):
        """
        Ustvari entiteto s podatki iz baze.
        """
        self = cls(*largs, **kwargs)
        self.__nastavi_id()
        return self

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
                        for stolpec in fields(cls) if stolpec.metadata
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
                                    if stolpec.metadata.get("glavni_kljuc"))
        return cls.GLAVNI_KLJUC

    @classmethod
    def _stolpci_uvoz(cls, stolpci):
        """
        Določi stolpce za vstavljanje pri uvozu.
        """
        return stolpci

    @classmethod
    def _vrstica_uvoz(cls, stolpci, vrstica):
        """
        Določi podatke za vstavljanje pri uvozu.
        """
        return zip(stolpci,
                   ((podatek if podatek else None) for podatek in vrstica))

    @classmethod
    def uvozi_podatke(cls):
        """
        Uvozi podatke v tabelo.
        """
        with open(f"podatki/{cls.tabela()}.csv") as f:
            rd = csv.reader(f)
            stolpci = cls._stolpci_uvoz(next(rd))
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
                    ), ({stolpec: podatek for stolpec, podatek
                         in cls._vrstica_uvoz(stolpci, vrstica)}
                        for vrstica in rd))
                    stevci = [stolpec.name for stolpec in fields(cls)
                              if stolpec.metadata.get("stevec")
                              and stolpec.name in stolpci]
                    if stevci:
                        cur.execute(sql.SQL("""
                                SELECT {stolpci} FROM {tabela};
                            """).format(stolpci=sql.SQL(", ").join(
                                            sql.SQL("MAX({stolpec})").format(
                                                stolpec=sql.Identifier(stolpec)
                                            )
                                            for stolpec in stevci
                                        ),
                                        tabela=sql.Identifier(cls.tabela())))
                        for stolpec, vrednost in zip(stevci, cur.fetchone()):
                            cur.execute(sql.SQL("""
                                    ALTER SEQUENCE {stevec} RESTART WITH {vrednost};
                                """).format(stevec=sql.Identifier(
                                                f"{cls.tabela()}_{stolpec}_seq"
                                            ),
                                            vrednost=sql.Literal(vrednost + 1)))

    @classmethod
    def _s_kljucem(cls, kljuc, id):
        """
        Vrni entiteto s podanim ključem.
        """
        with conn.cursor() as cur:
            cur.execute(sql.SQL("""
                SELECT {stolpci} FROM {tabela} {join}
                WHERE {kljuc} = {id}
                {zdruzevanje};
            """).format(
                stolpci=VEJICA.join(cls._stolpci()),
                tabela=cls._tabela(),
                join=cls._join(),
                kljuc=sql.Identifier(kljuc),
                id=sql.Literal(id),
                zdruzevanje=cls._zdruzevanje()
            ))
            vrstica = cur.fetchone()
            if not vrstica:
                raise ValueError(f'{cls.__name__} s ključem {id} ne obstaja!')
            return cls._objekt(vrstica)

    @classmethod
    def z_id(cls, id):
        """
        Vrni entiteto s podanim ID-jem.
        """
        return cls._s_kljucem(cls.glavni_kljuc().name, id)

    def vstavi(self):
        """
        Vstavi entiteto v tabelo.
        """
        stolpci = []
        podatki = []
        generirani = []
        for stolpec in fields(self):
            if not stolpec.metadata:
                continue
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
        try:
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
        except errors.IntegrityError:
            raise ValueError(f'Napaka pri vstavljanju {self.__class__.__name__} z ID-jem {id}!')
        except errors.DataError:
            raise TypeError(f'Napaka pri vstavljanju {self.__class__.__name__} z ID-jem {id}!')

    def posodobi(self):
        """
        Posodobi entiteto v bazi.
        """
        assert self.__dbid is not None, "Entiteta še ni v bazi!"
        try:
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
                            for stolpec in fields(self) if stolpec.metadata
                            for vrednost in [self[stolpec.name]]
                        ),
                        glavni_kljuc=sql.Identifier(self.glavni_kljuc().name),
                        id=sql.Literal(self.__dbid)
                    ))
                    self.__nastavi_id()
        except errors.IntegrityError:
            raise ValueError(f'Napaka pri posodabljanju {self.__class__.__name__} z ID-jem {id}!')
        except errors.DataError:
            raise TypeError(f'Napaka pri posodabljanju {self.__class__.__name__} z ID-jem {id}!')

    def izbrisi(self):
        """
        Izbriši entiteto iz baze.
        """
        assert self.__dbid is not None, "Entiteta še ni v bazi!"
        try:
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
        except errors.IntegrityError:
            raise ValueError(f'Napaka pri brisanju {self.__class__.__name__} z ID-jem {id}!')

    @classmethod
    def izbrisi_id(cls, id):
        """
        Izbriši entiteto s podanim ID-jem iz baze.
        """
        cls.iz_baze(**{cls.glavni_kljuc().name: id}).izbrisi()

    @Seznam
    @classmethod
    def seznam(cls, cur):
        """
        Vrni seznam entitet iz baze.
        """
        yield from (cls._objekt(vrstica) for vrstica in cur)

    @seznam.poizvedba
    def seznam(cls):
        """
        Sestavi poizvedbo za seznam entitet iz baze.
        """
        return dict(
            stolpci=VEJICA.join(cls._stolpci()),
            tabela=cls._tabela(),
            join=cls._join(),
            zdruzevanje=cls._zdruzevanje(),
            urejanje=cls._urejanje()
        )

    @classmethod
    def _stolpci(cls):
        """
        Vrni zaporedje stolpcev za branje iz baze.
        """
        yield from (sql.Identifier(stolpec.name) for stolpec in fields(cls)
                    if stolpec.metadata)

    @classmethod
    def _tabela(cls):
        """
        Vrni izraz za tabelo za branje iz baze.
        """
        return sql.Identifier(cls.tabela())

    @classmethod
    def _join(cls):
        """
        Vrni izraz za pridruževanje podatkov za združevanje.
        """
        return PRAZNO

    @classmethod
    def _zdruzevanje(cls):
        """
        Vrni izraz za združevanje za branje iz baze.
        """
        return PRAZNO

    @classmethod
    def _urejanje(cls):
        """
        Vrni izraz za urejanje pri branju iz baze.
        """
        return sql.SQL("""
            ORDER BY {tabela}.{stolpec}
        """).format(
            tabela=sql.Identifier(cls.tabela()),
            stolpec=sql.Identifier(cls.glavni_kljuc().name)
        )

    @classmethod
    def _objekt(cls, vrstica):
        """
        Vrni objekt po branju iz baze.
        """
        return cls.iz_baze(*vrstica)

    def slovar(self):
        """
        Vrni slovar s polji entitete.
        """
        return {stolpec.name: self[stolpec.name] for stolpec in fields(self)
                if stolpec.metadata and not stolpec.metadata["skrit"]}

    def posodobi_polja(self, **polja):
        """
        Posodobi podana polja.
        """
        for polje, vrednost in polja.items():
            setattr(self, polje, vrednost)
