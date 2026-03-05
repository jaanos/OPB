-- banka_vaje.sql
-- Skice resitev za Nalogo 2 (ORDER BY, LIMIT) in Nalogo 3 (GROUP BY)
-- Predpostavka: povezava je na bazo banka2025_uporabnik.

/* ============================================================
   NALOGA 2: ORDER BY, LIMIT
   ============================================================ */

-- 1) Seznam vseh krajev, urejen po imenu kraja.
-- Opomba: za preverjanje vrstnega reda sumnikov lahko po potrebi dodas COLLATE.
SELECT posta, kraj
FROM kraj



ORDER BY kraj ASC;


-- 2) Seznam vseh oseb, urejen v padajocem vrstnem redu po datumu rojstva.
-- Padajoce po rojstvu => od najmlajsih proti najstarejsim.
SELECT emso, ime, priimek, rojstvo, ulica, posta
FROM oseba
ORDER BY rojstvo DESC;


-- 3) Izpis najmlajsega komitenta banke.
SELECT emso, ime, priimek, rojstvo
FROM oseba
ORDER BY rojstvo DESC
LIMIT 1;


-- 4) Tri transakcije, pri katerih se je obrnilo najvec denarja.
-- Uporabimo ABS(znesek), da stevilo primerja po absolutni vrednosti.
SELECT id, racun, znesek, cas, opis
FROM transakcija
ORDER BY ABS(znesek) DESC
LIMIT 3;


-- 5) Skica za server-side pagination.
-- Ideja: aplikacija poda velikost strani (:page_size) in stevilko strani (:page_number, zacetek pri 1).
-- OFFSET = (:page_number - 1) * :page_size
-- Primer na tabeli transakcija (najnovejse najprej):
SELECT id, racun, znesek, cas, opis
FROM transakcija
ORDER BY cas DESC, id DESC
LIMIT :page_size
OFFSET (:page_number - 1) * :page_size;

-- Alternativa s konkretnimi vrednostmi (npr. stran 2, velikost 20):
-- LIMIT 20 OFFSET 20;


/* ============================================================
   NALOGA 3: GROUP BY
   ============================================================ */

-- 1) Stevilo oseb v vsakem kraju.
-- Zahtevan izpis: posta, stevilo narocnikov (oseb).
SELECT posta, COUNT(*) AS stevilo_oseb
FROM oseba
GROUP BY posta
ORDER BY posta;


-- 2) Trenutno stanje na racunih oseb (brez obresti).
-- Zahtevan izpis: stevilka racuna, trenutno stanje.
-- LEFT JOIN zagotovi, da vidimo tudi racune brez transakcij (stanje 0).
SELECT r.stevilka,
       COALESCE(SUM(t.znesek), 0) AS stanje
FROM racun r
LEFT JOIN transakcija t ON t.racun = r.stevilka
GROUP BY r.stevilka
ORDER BY r.stevilka;


-- 3) Trenutno stanje na racunih oseb + podatki o lastniku.
-- Zahtevan izpis: stevilka racuna, ime, priimek, trenutno stanje.
SELECT r.stevilka,
       o.ime,
       o.priimek,
       COALESCE(SUM(t.znesek), 0) AS stanje
FROM racun r
JOIN oseba o ON o.emso = r.lastnik
LEFT JOIN transakcija t ON t.racun = r.stevilka
GROUP BY r.stevilka, o.ime, o.priimek
ORDER BY r.stevilka;


-- 4) Enako kot (3), urejeno po trenutnem stanju padajoce.
SELECT r.stevilka,
       o.ime,
       o.priimek,
       COALESCE(SUM(t.znesek), 0) AS stanje
FROM racun r
JOIN oseba o ON o.emso = r.lastnik
LEFT JOIN transakcija t ON t.racun = r.stevilka
GROUP BY r.stevilka, o.ime, o.priimek
ORDER BY stanje DESC, r.stevilka;

select racun, o.ime, o.priimek, sum(znesek) from transakcija
join racun r on r.stevilka = transakcija.racun
JOIN oseba o on o.emso = r.lastnik
group by racun, o.ime, o.priimek
HAVING sum(znesek) > 1000

