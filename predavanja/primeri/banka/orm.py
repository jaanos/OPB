from psycopg import connect, sql, errors
import csv


def povezi(*largs, **kwargs):
    """
    Vzpostavi povezavo z bazo.
    """
    global conn
    conn = connect(*largs, **kwargs, autocommit=True)
    return conn


class Stolpec:
    """
    Razred za definicije stolpcev.
    """

    def __init__(self, tip, lastnosti="", privzeto=None, referenca=None):
        """
        Definiraj stolpec.
        """
        self.tip = tip
        self.lastnosti = lastnosti
        self.privzeto = privzeto
        self.referenca = referenca

    def __repr__(self):
        """
        Predstavi definicijo stolpca v znakovni obliki.
        """
        return f'<{self.__class__.__name__}: {self}>'

    def __str__(self):
        """
        Predstavi definicijo stolpca v obliki za izpis.
        """
        return self.definicija().as_string(conn).strip()

    def definicija(self, glavni_kljuc=False):
        """
        Vrni niz SQL z definicijo stolpca.
        """
        return sql.SQL("{tip} {kljuc} {lastnosti} {privzeto} {referenca}").format(
            tip=sql.SQL(self.tip),
            kljuc=sql.SQL("PRIMARY KEY" if glavni_kljuc else ""),
            lastnosti=sql.SQL(self.lastnosti),
            privzeto=sql.SQL(
                    "DEFAULT {vrednost}"
                ).format(vrednost=sql.SQL(self.privzeto))
                if self.privzeto else sql.SQL(""),
            referenca=sql.SQL("REFERENCES {tabela}({stolpec})").format(
                    tabela=sql.Identifier(self.referenca.TABELA),
                    stolpec=sql.Identifier(self.referenca.GLAVNI_KLJUC)
                )
                if self.referenca else sql.SQL("")
        )


def lastnost_reference(polje, entiteta):
    """
    Vrni lastnost za stolpec z referenco.
    """

    @property
    def referenca(self):
        """
        Vrni entiteto, na katero se stolpec sklicuje.
        """
        vrednost = getattr(self, polje)
        if vrednost is None:
            vrednost = entiteta.NULL
            setattr(self, polje, vrednost)
        elif not isinstance(vrednost, Entiteta):
            vrednost = entiteta.z_id(vrednost)
            setattr(self, polje, vrednost)
        return vrednost

    @referenca.setter
    def referenca(self, vrednost):
        """
        Nastavi novo vrednost sklica.
        """
        setattr(self, polje, vrednost)

    return referenca


class Entiteta:
    """
    Nadrazred za posamezne entitetne tipe.
    """

    def __init__(self, /, *largs, **kwargs):
        """
        Inicializiraj posamezno entiteto.
        """
        stolpci = iter(self.STOLPCI)
        for vrednost in largs:
            setattr(self, next(stolpci), vrednost)
        for stolpec in stolpci:
            setattr(self, stolpec, kwargs.pop(stolpec, None))
        assert not kwargs, "Podani so odvečni ali podvojeni argumenti!"
        self.__dbid = self.glavni_kljuc()

    def __bool__(self):
        """
        Vrni resničnostno vrednost za entiteto.
        """
        return self.glavni_kljuc() is not None

    def __getitem__(self, stolpec):
        """
        Vrni vrednost v stolpcu v obliki, kot je zapisana v bazi.
        """
        if self.STOLPCI[stolpec].referenca:
            vrednost = getattr(self, f'_{stolpec}')    
            if isinstance(vrednost, Entiteta):
                vrednost = vrednost.glavni_kljuc()
        else:
            vrednost = getattr(self, stolpec)
        return vrednost

    def __iter__(self):
        """
        Iteriraj po vrednostih stolpcev v obliki, kot so zapisane v bazi.
        """
        for stolpec in self.STOLPCI:
            yield self[stolpec]

    def __repr__(self):
        """
        Predstavi entiteto v znakovni obliki.
        """
        return f'<{self.__class__.__name__}: {self}>'

    def __str__(self):
        """
        Predstavi entiteto v obliki za izpis.
        """
        return str(list(self))

    def __init_subclass__(cls, /, **kwargs):
        """
        Inicializiraj polja podrazreda.
        """
        super().__init_subclass__(**kwargs)
        assert cls.GLAVNI_KLJUC in cls.STOLPCI, \
            "Glavni ključ ni naveden med stolpci!"
        for ime, stolpec in cls.STOLPCI.items():
            if stolpec.referenca:
                setattr(cls, ime,
                        lastnost_reference(f'_{ime}', stolpec.referenca))
        cls.NULL = cls()

    @classmethod
    def __tabela_kljuc(cls):
        """
        Vrni slovar z imenom tabele in glavnim ključem.
        """
        return dict(tabela=sql.Identifier(cls.TABELA),
                    kljuc=sql.Identifier(cls.GLAVNI_KLJUC))

    @classmethod
    def ustvari(cls, *largs, **kwargs):
        """
        Ustvari nov primerek entitete za dodajanje v bazo.
        """
        self = cls(*largs, **kwargs)
        self.__dbid = None
        return self

    @classmethod
    def izbrisi_tabelo(cls, ohrani=True):
        """
        Izbriši tabelo iz baze.
        """
        with conn.cursor() as cur:
            cur.execute(sql.SQL("""
                    DROP TABLE {ohrani} {tabela};
                """).format(ohrani=sql.SQL("IF EXISTS" if ohrani
                                            else ""),
                            tabela=sql.Identifier(cls.TABELA)))

    @classmethod
    def ustvari_tabelo(cls, izbrisi=False, ohrani=False):
        """
        Ustvari tabelo v bazi.
        """
        with conn.cursor() as cur:
            with conn.transaction():
                if izbrisi:
                    cls.izbrisi_tabelo(ohrani=ohrani)
                cur.execute(sql.SQL("""
                        CREATE TABLE {ohrani} {tabela} ({stolpci});
                    """).format(ohrani=sql.SQL("IF NOT EXISTS" if ohrani
                                                else ""),
                                tabela=sql.Identifier(cls.TABELA),
                                stolpci=sql.SQL(", ").join(
                                    sql.SQL("{stolpec} {definicija}").format(
                                        stolpec=sql.Identifier(ime),
                                        definicija=stolpec.definicija(
                                            cls.GLAVNI_KLJUC == ime
                                        )
                                    )
                                    for ime, stolpec in cls.STOLPCI.items()
                                )))

    @classmethod
    def uvozi_podatke(cls):
        """
        Uvozi podatke v tabelo.
        """
        with open(f'podatki/{cls.TABELA}.csv', encoding="UTF-8") as f:
            rd = csv.reader(f)
            stolpci = next(rd)
            with conn.cursor() as cur:
                with conn.transaction():
                    cur.executemany(sql.SQL("""
                            INSERT INTO {tabela} ({stolpci})
                            VALUES ({vrednosti});
                        """).format(tabela=sql.Identifier(cls.TABELA),
                                    stolpci=sql.SQL(", ").join(
                                        sql.Identifier(stolpec)
                                        for stolpec in stolpci
                                    ),
                                    vrednosti=sql.SQL(", ").join(
                                        sql.Placeholder(stolpec)
                                        for stolpec in stolpci
                                    )),
                        ({stolpec: vrednost if vrednost else None
                                for stolpec, vrednost in zip(stolpci, vrstica)}
                            for vrstica in rd))
                    serial = [ime for ime, stolpec in cls.STOLPCI.items()
                                if stolpec.tip == "SERIAL"]
                    if serial:
                        cur.execute(sql.SQL("""
                                SELECT {stolpci} FROM {tabela};
                            """).format(stolpci=sql.SQL(", ").join(
                                            sql.SQL("MAX({stolpec})").format(
                                                stolpec=sql.Identifier(stolpec)
                                            )
                                            for stolpec in serial
                                        ),
                                        tabela=sql.Identifier(cls.TABELA)))
                        for stolpec, vrednost in zip(serial, cur.fetchone()):
                            cur.execute(sql.SQL("""
                                    ALTER SEQUENCE {stevec} RESTART WITH {vrednost};
                                """).format(stevec=sql.Identifier(
                                                f"{cls.TABELA}_{stolpec}_seq"
                                            ),
                                            vrednost=sql.Literal(vrednost + 1)))

    @classmethod
    def _parametri(cls, **kwargs):
        """
        Vrni parametre za pridobivanje podatkov iz baze.
        """
        parametri = cls.__tabela_kljuc()
        parametri.update(
            stolpci=sql.SQL(", ").join(
                sql.Identifier(stolpec) for stolpec in cls.STOLPCI
            ),
            urejanje=parametri['kljuc'],
            zdruzevanje=None
        )
        parametri.update(kwargs)
        for polje, beseda in (
                    ('stolpci', ""),
                    ('urejanje', "ORDER BY"),
                    ('zdruzevanje', "GROUP BY")
                ):
            if parametri[polje] is None:
                parametri[polje] = sql.SQL("")
            else:
                stolpci = parametri[polje]
                if not isinstance(stolpci, (list, tuple)):
                    stolpci = [stolpci]
                parametri[polje] = sql.SQL(
                    "{beseda} {stolpci}"
                ).format(
                    beseda=sql.SQL(beseda),
                    stolpci=sql.SQL(", ").join(
                        stolpec if isinstance(stolpec, sql.Composable)
                        else sql.Identifier(stolpec)
                        for stolpec in stolpci
                    )
                )
        return parametri

    @classmethod
    def _iz_baze(cls, *vrstica):
        """
        Ustvari entiteto s podatki iz baze.
        """
        return cls(*vrstica)

    @classmethod
    def z_id(cls, id):
        """
        Vrni entiteto s podanim ID-jem.
        """
        with conn.cursor() as cur:
            cur.execute(sql.SQL("""
                    SELECT {stolpci} FROM {tabela}
                     WHERE {kljuc} = %s
                    {zdruzevanje};
                """).format(**cls._parametri()), [id])
            vrstica = cur.fetchone()
            if not vrstica:
                raise ValueError(f'{cls.__name__} z ID-jem {id} ne obstaja!')
            return cls._iz_baze(*vrstica)

    @classmethod
    def seznam(cls, urejanje=None, /, **kwargs):
        """
        Vračaj entitete iz baze.
        """
        urejanje = {} if urejanje is None else dict(urejanje=urejanje)
        with conn.cursor() as cur:
            cur.execute(sql.SQL("""
                    SELECT {stolpci} FROM {tabela}
                    {filtriranje}
                    {zdruzevanje}
                    {urejanje};
                """).format(**cls._parametri(**urejanje),
                            filtriranje=sql.SQL("WHERE {pogoji}").format(
                                pogoji=sql.SQL(" AND ").join(
                                    sql.SQL(
                                        "{stolpec} = {vrednost}"
                                    ).format(
                                        stolpec=sql.Identifier(stolpec),
                                        vrednost=sql.Placeholder(stolpec)
                                    )
                                    for stolpec in kwargs
                                )
                            ) if kwargs else sql.SQL("")),
                            {
                                stolpec: vrednost.glavni_kljuc()
                                    if isinstance(vrednost, Entiteta)
                                    else vrednost
                                for stolpec, vrednost in kwargs.items()
                            })
            for vrstica in cur:
                yield cls._iz_baze(*vrstica)

    def glavni_kljuc(self):
        """
        Vrni glavni ključ entitete.
        """
        return self[self.GLAVNI_KLJUC]

    def shrani(self):
        """
        Shrani entiteto v bazo.
        """
        try:
            with conn.cursor() as cur:
                with conn.transaction():
                    for ime, stolpec in self.STOLPCI.items():
                        if not stolpec.referenca:
                            continue
                        vrednost = getattr(self, f'_{ime}')
                        if isinstance(vrednost, Entiteta):
                            vrednost.shrani()
                    vrednosti = self.vrednosti()
                    tabela_kljuc = self.__tabela_kljuc()
                    if self.__dbid:
                        cur.execute(sql.SQL("""
                                UPDATE {tabela} SET {vrednosti}
                                WHERE {kljuc} = %(__dbid)s;
                            """).format(vrednosti=sql.SQL(", ").join(
                                            sql.SQL(
                                                "{stolpec} = {vrednost}"
                                            ).format(
                                                stolpec=sql.Identifier(stolpec),
                                                vrednost=sql.Placeholder(stolpec)
                                            )
                                            for stolpec in vrednosti
                                        ),
                                        **tabela_kljuc),
                            {**vrednosti, "__dbid": self.__dbid})
                    else:
                        generirani = {ime for ime, stolpec in self.STOLPCI.items()
                                        if (stolpec.privzeto or
                                            stolpec.tip == "SERIAL")
                                        and vrednosti[ime] is None}
                        vrednosti = {ime: vrednost for ime, vrednost
                                        in vrednosti.items()
                                        if ime not in generirani}
                        stolpci = list(vrednosti)
                        generirani = list(generirani)
                        cur.execute(sql.SQL("""
                                INSERT INTO {tabela} ({stolpci})
                                VALUES ({vrednosti})
                                {generirani};
                            """).format(stolpci=sql.SQL(", ").join(
                                            sql.Identifier(stolpec)
                                            for stolpec in stolpci
                                        ),
                                        vrednosti=sql.SQL(", ").join(
                                            sql.Placeholder(stolpec)
                                            for stolpec in stolpci
                                        ),
                                        generirani=sql.SQL(
                                                "RETURNING {generirani}"
                                            ).format(generirani=sql.SQL(", ").join(
                                                sql.Identifier(stolpec)
                                                for stolpec in generirani
                                            ))
                                            if generirani else sql.SQL(""),
                                        **tabela_kljuc),
                            vrednosti)
                        if generirani:
                            for stolpec, vrednost in zip(generirani, cur.fetchone()):
                                setattr(self, stolpec, vrednost)
                    self.__dbid = self.glavni_kljuc()
        except errors.IntegrityError:
            raise ValueError
        except errors.DataError:
            raise TypeError

    @classmethod
    def izbrisi_id(cls, id):
        """
        Izbriši entiteto z danim ID-jem iz baze.
        """
        try:
            with conn.cursor() as cur:
                cur.execute(sql.SQL("""
                        DELETE FROM {tabela} WHERE {kljuc} = %s;
                    """).format(**cls.__tabela_kljuc()), [id])
        except errors.IntegrityError:
            raise ValueError

    def izbrisi(self):
        """
        Izbriši entiteto iz baze.
        """
        self.izbrisi_id(self.glavni_kljuc())
        self.__dbid = None

    def vrednosti(self):
        """
        Vrni slovar vrednosti stolpcev v obliki, kot so zapisane v bazi.
        """
        return {ime: self[ime] for ime in self.STOLPCI}

    def posodobi(self, /, **kwargs):
        """
        Posodobi vrednosti stolpcev s podanimi vrednostmi.
        """
        assert all(polje in self.STOLPCI for polje in kwargs), \
            "Podani so odvečni argumenti!"
        for polje, vrednost in kwargs.items():
            setattr(self, polje, vrednost)
        return self
