import bcrypt
from auth import auth
from orm import povezi, Entiteta, Stolpec, sql


class Kraj(Entiteta):
    """
    Kraj z lastnostmi:
    - posta: poštna številka (glavni ključ)
    - kraj: ime kraja
    """

    TABELA = "kraj"
    STOLPCI = {
        "posta": Stolpec("INTEGER"),
        "kraj": Stolpec("TEXT", "NOT NULL")
    }
    GLAVNI_KLJUC = "posta"

    def __str__(self):
        """
        Predstavi kraj v obliki za izpis.
        """
        return f'{self.posta} {self.kraj}'


class Oseba(Entiteta):
    """
    Oseba z lastnostmi:
    - ime: ime osebe
    - priimek: priimek osebe
    - emso: EMŠO osebe (glavni ključ)
    - naslov: naslov osebe
    - kraj_id: kraj osebe (predstavljen s poštno številko)
    """

    TABELA = "oseba"
    STOLPCI = {
        "ime": Stolpec("TEXT", "NOT NULL"),
        "priimek": Stolpec("TEXT", "NOT NULL"),
        "emso": Stolpec("TEXT"),
        "naslov": Stolpec("TEXT", "NOT NULL"),
        "kraj_id": Stolpec("INTEGER", "NOT NULL", referenca=Kraj),
        "up_ime": Stolpec("TEXT", "UNIQUE",
            privzeto_uvoz=lambda cls, o: (o["ime"][0] + o["priimek"]).lower()),
        "geslo": Stolpec("BYTEA",
            privzeto_uvoz=lambda cls, o: cls._nastavi_geslo(o["up_ime"])),
        "admin": Stolpec("BOOLEAN", "NOT NULL", privzeto="FALSE",
            privzeto_uvoz=lambda cls, o: (o["emso"] == '1'))
    }
    GLAVNI_KLJUC = "emso"

    def __str__(self):
        """
        Predstavi osebo v obliki za izpis.
        """
        return f'{self.ime} {self.priimek} ({self.emso})'

    @classmethod
    def _parametri(cls, urejanje=None):
        """
        Vrni parametre za pridobivanje podatkov iz baze.
        """
        return super()._parametri(
            stolpci=["ime", "priimek", "emso", "naslov", "posta", "kraj",
                        "up_ime", "geslo", "admin"],
            tabela=sql.SQL("oseba JOIN kraj ON kraj_id = posta"),
            urejanje=["priimek", "ime", "emso"]
                if urejanje is None else urejanje
        )

    @classmethod
    def _iz_baze(cls, ime, priimek, emso, naslov, posta, kraj, up_ime, geslo,
                    admin):
        """
        Ustvari osebo s podatki iz baze.
        """
        return cls(ime, priimek, emso, naslov, Kraj(posta, kraj), up_ime,
                    geslo, admin)

    @classmethod
    def z_uporabniskim_imenom(cls, up_ime):
        """
        Vrni uporabnika z navedenim uporabniškim imenom.
        """
        try:
            return next(cls.seznam(up_ime=up_ime))
        except StopIteration:
            return cls.ustvari(up_ime=up_ime)

    def vrednosti(self, vse=False):
        """
        Vrni slovar vrednosti stolpcev (brez gesla) v obliki,
        kot so zapisane v bazi.
        """
        return super().vrednosti(vse=vse, izpusti=('geslo', ))

    @staticmethod
    def _nastavi_geslo(geslo):
        """
        Vrni zgostitev podanega gesla.
        """
        geslo = geslo.encode("utf-8")
        sol = bcrypt.gensalt()
        return bcrypt.hashpw(geslo, sol)

    def nastavi_geslo(self, geslo):
        """
        Nastavi podano geslo.
        """
        self.geslo = self._nastavi_geslo(geslo)

    @staticmethod
    def _preveri_geslo(geslo, zgostitev):
        """
        Preveri podano geslo glede na podano zgostitev.
        """
        geslo = geslo.encode("utf-8")
        return bcrypt.checkpw(geslo, zgostitev)

    def preveri_geslo(self, geslo):
        """
        Preveri podano geslo.
        """
        return self._preveri_geslo(geslo, self.geslo)

    def racuni(self):
        """
        Vračaj račune osebe.
        """
        with conn.cursor() as cur:
            cur.execute("""
                    SELECT stevilka, COALESCE(SUM(znesek), 0)
                      FROM racun
                      LEFT JOIN transakcija ON stevilka = racun_id
                     WHERE oseba_id = %s
                     GROUP BY stevilka
                     ORDER BY stevilka;
                """, [self.emso])
            for stevilka, stanje in cur:
                yield Racun(stevilka, self, stanje=stanje)


class Racun(Entiteta):
    """
    Račun z lastnostmi:
    - stevilka: številka računa (glavni ključ)
    - oseba_id: lastnik računa (predstavljen z EMŠOm)
    """

    TABELA = "racun"
    STOLPCI = {
        "stevilka": Stolpec("SERIAL"),
        "oseba_id": Stolpec("TEXT", "NOT NULL", referenca=Oseba)
    }
    GLAVNI_KLJUC = "stevilka"

    def __init__(self, *largs, stanje=None, **kwargs):
        """
        Inicializiraj račun.
        """
        super().__init__(*largs, **kwargs)
        self.stanje = stanje

    def __str__(self):
        """
        Predstavi račun v obliki za izpis.
        """
        return f'Račun {self.stevilka} osebe z EMŠOm {self["oseba_id"]}'

    @classmethod
    def _parametri(cls, urejanje=None):
        """
        Vrni parametre za pridobivanje podatkov iz baze.
        """
        return super()._parametri(
            stolpci=["ime", "priimek", "emso", "stevilka",
                        sql.SQL("COALESCE(SUM(znesek), 0)")],
            tabela=sql.SQL("""
                    oseba JOIN racun ON emso = oseba_id
                     LEFT JOIN transakcija ON stevilka = racun_id
                """),
            zdruzevanje=sql.SQL("stevilka, emso"),
            urejanje="stevilka" if urejanje is None else urejanje
        )

    @classmethod
    def _iz_baze(cls, ime, priimek, emso, stevilka, stanje):
        """
        Ustvari račun s podatki iz baze.
        """
        return cls(stevilka, Oseba(ime, priimek, emso), stanje=stanje)

    def transakcije(self):
        """
        Vračaj transakcije na računu.
        """
        with conn.cursor() as cur:
            cur.execute("""
                    SELECT id, znesek, cas, opis
                      FROM transakcija
                     WHERE racun_id = %s
                     ORDER BY cas;
                """, [self.stevilka])
            for id, znesek, cas, opis in cur:
                yield Transakcija(id, znesek, self, cas, opis)


class Transakcija(Entiteta):
    """
    Transakcija z lastnostmi:
    - id: ID transakcije (glavni ključ)
    - znesek: nakazani znesek
    - racun_id: račun transakcije (predstavljen s številko računa)
    - cas: čas transakcije
    - opis: opis transakcije
    """

    TABELA = "transakcija"
    STOLPCI = {
        "id": Stolpec("SERIAL"),
        "znesek": Stolpec("INTEGER", "NOT NULL"),
        "racun_id": Stolpec("INTEGER", "NOT NULL", referenca=Racun),
        "cas": Stolpec("TIMESTAMP(0)", "NOT NULL", privzeto="NOW()"),
        "opis": Stolpec("TEXT")
    }
    GLAVNI_KLJUC = "id"

    def __str__(self):
        """
        Predstavi transakcijo v obliki za izpis.
        """
        return f'Transakcija {self.id} na računu {self["racun_id"]} ' \
               f'z zneskom {self.znesek}'


ENTITETE = (Kraj, Oseba, Racun, Transakcija)


def ustvari_bazo(izbrisi=False, ohrani=True):
    """
    Ustvari tabele v bazi.
    """
    with conn.transaction():
        if izbrisi:
            for entiteta in reversed(ENTITETE):
                entiteta.izbrisi_tabelo(ohrani=ohrani)
        for entiteta in ENTITETE:
            entiteta.ustvari_tabelo(ohrani=ohrani)


def uvozi_podatke():
    """
    Uvozi podatke v tabele.
    """
    with conn.transaction():
        for entiteta in ENTITETE:
            entiteta.uvozi_podatke()


def vzpostavi_povezavo():
    """
    Vzpostavi povezavo z bazo in jo inicializiraj.
    """
    global conn
    conn = povezi(**auth)
    ustvari_bazo()
    return conn
