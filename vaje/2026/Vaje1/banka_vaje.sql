-- ============================================================
-- NALOGA 3: INSERT
-- ============================================================

-- 1) Po potrebi dodaj kraj (ce ga se ni).

-- Preverimo, kateri kraji so ze v tabeli kraj.
select * from kraj;

-- Po potrebi dodamo kraj s posto 1370 Logatec
INSERT INTO kraj (posta, kraj)
VALUES (1370, 'Logatec')


-- 2) Vpis osebe.
-- POZOR: emso je TEXT, zato ga pisi v enojnih navednicah.
INSERT INTO oseba (emso, ime, priimek, rojstvo, ulica, posta)
VALUES ('0505995500123', 'Gašper Domen', 'Romih', '1995-05-05', 'Neka ulica 13', 1370);

-- 3) Ustvari svoj racun.
-- stevilka se generira samodejno (sequence rstevec), zato je ne podamo.
select * from oseba

-- Returning lahko uporabimi, da nam vrne število računa,
-- ki je bila ustvarjena.  V vsakem primeru jo lahko dobimo
-- z primerno poizvedbo.
INSERT INTO racun (lastnik)
VALUES ('0505995500123') RETURNING stevilka;

-- 4) Dodaj nekaj transakcij (vsaj 2 pologa in 2 dviga).
-- Variant A: racun poisces po lastniku

select * from racun where lastnik = '0505995500123';

INSERT INTO transakcija (znesek, racun, opis)
Values (1000, 100001, 'plača januar');

INSERT INTO transakcija (znesek, racun, opis)
Values (15, 100001, 'flik vračilo za kosilo');

INSERT INTO transakcija (znesek, racun, opis)
Values (-10, 100001, 'kosilo itd');

INSERT INTO transakcija (znesek, racun, opis)
Values (-600, 100001, 'rezervacija smučanje')

SELECT * from transakcija
--WHERE racun = 100001;






-- ============================================================
-- NALOGA 4: UPDATE
-- ============================================================

-- A) Poskus spremembe EMŠO.

-- UPDATE ukaz:

-- UPDATE tabela
-- SET stolpec1 = vrednost1, stolpec2 = vrednost2, ...
-- WHERE pogoj;

-- Če ni WHERE pogoja, se update naredi na vseh vrsticah v tabeli!

UPDATE oseba
SET emso = '0505995500124'
WHERE emso = '0505995500123';

-- B) Primer spremembe drugega polja (to praviloma uspe).
select * from oseba

UPDATE oseba
SET ulica = 'Nova ulica 42', rojstvo = '1995-05-06'
WHERE emso = '0505995500123';


-- ============================================================
-- NALOGA 5: DELETE
-- ============================================================

-- Zbrisi eno transakcijo (npr. zadnjo na tvojem racunu).

select * from transakcija
WHERE racun = 100001

-- Where pogoj je izredno pomemben, druge izbrišemo
-- vse podatke v tabeli
delete from transakcija
WHERE id = 22;


-- ============================================================
-- NALOGA 6: SELECT
-- ============================================================

-- 1) Vse osebe, ki zivijo v kraju s posto 1000.
SELECT *
FROM oseba
WHERE posta = 1000;

-- 2) Vse osebe, samo ime, priimek, posta.
SELECT ime, priimek, posta
FROM oseba;

-- 3) Vse transakcije z zneskom < -1000.
SELECT *
FROM transakcija
WHERE znesek < -1000;

-- Mogoče to ni čisto pravilno!
-- Spodnja poizvedba vrne vse transakcije,
-- kjer smo porabili največ 1000 EUR
SELECT *
FROM transakcija
WHERE znesek >= -1000 AND znesek < 0;


-- 4) Enako kot 3), znesek zaokrozen na najblizjo stotico proti nicli.
-- Pri celostevilskem deljenju v PostgreSQL je deljenje z integer "trunc" proti nicli.
-- Ko imamo stolpce, ki je "izračun", moramo poveati njegovo ime 
-- To storimo z AS ukazom, ki mu sledi ime tolpca
SELECT
  id,
  (znesek / 100) * 100 AS znesek_na_stotico_proti_nicli,
  racun,
  cas,
  opis
FROM transakcija
WHERE znesek < -1000;

-- 5) Vse osebe, samo ime, priimek in ime kraja.
SELECT o.ime, o.priimek, k.kraj
FROM oseba o
JOIN kraj k ON k.posta = o.posta;

-- 6) Vse osebe iz kraja Ljubljana (posta iz tabele kraj).
SELECT o.*
FROM oseba o
JOIN kraj k ON k.posta = o.posta
WHERE k.kraj = 'Ljubljana';

-- 7) Koliko racunov je odprtih na banki.
SELECT COUNT(*) AS st_racunov
FROM racun;

-- 8) Koliko oseb zivi v kraju s posto 1000.
SELECT COUNT(*) AS st_oseb_v_1000
FROM oseba
WHERE posta = 1000;

-- 9) Koliko denarja je trenutno v banki (vsota vseh transakcij).
SELECT COALESCE(SUM(znesek), 0) AS denar_v_banki
FROM transakcija;

-- 10) Koliko denarja imas trenutno na svojem racunu.
SELECT COALESCE(SUM(t.znesek), 0) AS stanje_moj_racun
FROM transakcija t
JOIN racun r ON r.stevilka = t.racun
WHERE r.lastnik = '0505995500123';

-- 11) Imena in priimki oseb, ki imajo vsaj eno transakcijo z |znesek| >= 1000.
SELECT DISTINCT o.ime, o.priimek
FROM oseba o
JOIN racun r ON r.lastnik = o.emso
JOIN transakcija t ON t.racun = r.stevilka
WHERE ABS(t.znesek) >= 1000;

