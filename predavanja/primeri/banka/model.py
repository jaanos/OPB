from auth import auth
from orm import povezi, Entiteta, Stolpec


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
        "kraj_id": Stolpec("INTEGER", "NOT NULL", referenca=Kraj)
    }
    GLAVNI_KLJUC = "emso"

    def __str__(self):
        """
        Predstavi osebo v obliki za izpis.
        """
        return f'{self.ime} {self.priimek} ({self.emso})'

    @classmethod
    def seznam(cls):
        """
        Vračaj osebe iz baze.
        """
        with conn.cursor() as cur:
            cur.execute("""
                    SELECT ime, priimek, emso, naslov, posta, kraj
                    FROM oseba JOIN kraj ON kraj_id = posta;
                """)
            for ime, priimek, emso, naslov, posta, kraj in cur:
                yield cls(ime, priimek, emso, naslov, Kraj(posta, kraj))

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
        super().__init__(*largs, **kwargs)
        self.stanje = stanje

    def __str__(self):
        """
        Predstavi račun v obliki za izpis.
        """
        return f'Račun {self.stevilka} osebe z EMŠOm {self["oseba_id"]}'

    @classmethod
    def seznam(cls):
        """
        Vračaj račune iz baze.
        """
        with conn.cursor() as cur:
            cur.execute("""
                    SELECT ime, priimek, emso, stevilka,
                    COALESCE(SUM(znesek), 0)
                    FROM oseba JOIN racun ON emso = oseba_id
                    LEFT JOIN transakcija ON stevilka = racun_id
                    GROUP BY stevilka, emso
                    ORDER BY stevilka;
                """)
            for ime, priimek, emso, stevilka, stanje in cur:
                yield cls(stevilka, Oseba(ime, priimek, emso), stanje=stanje)

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
        "cas": Stolpec("TIMESTAMP", "NOT NULL", privzeto="NOW()"),
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
