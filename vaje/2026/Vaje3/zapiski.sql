-- Vaje (3. teden): JOIN, GROUP BY, HAVING
-- Baza: traktorji (oseba, otroci, znamka, traktor, deli)

-- =====================
-- JOIN
-- =====================

-- 1) Izpiši imena oseb brez traktorjev.
SELECT o.ime
FROM oseba o
LEFT JOIN traktor t ON t.lastnik = o.id
WHERE t.id IS NULL;

-- 2) Izpiši vse veljavne pare (ime starša, ime otroka).
SELECT s.ime AS stars,
       ot.ime AS otrok
FROM otroci rel
JOIN oseba s  ON s.id = rel.stars
JOIN oseba ot ON ot.id = rel.otrok;

-- 3) Izpiši starše, ki so svojim otrokom kupili traktor,
--    še preden so ti dopolnili 10 let.
SELECT DISTINCT s.ime AS stars
FROM otroci rel
JOIN oseba s  ON s.id = rel.stars
JOIN oseba ot ON ot.id = rel.otrok
JOIN traktor t ON t.lastnik = rel.otrok
WHERE t.nakup < (ot.rojstvo + '10 years'::INTERVAL);

-- 4) Izpiši vse pare (ime osebe, ime starega starša).
--    Za osebe brez starih staršev izpiši (ime osebe, NULL).
SELECT o.ime AS oseba,
       stari.ime AS stari_stars
FROM oseba o
LEFT JOIN otroci p_rel ON p_rel.otrok = o.id
LEFT JOIN otroci gp_rel ON gp_rel.otrok = p_rel.stars
LEFT JOIN oseba stari ON stari.id = gp_rel.stars;

-- 4) DODATNO: celotna rodovna linija z uporabo CTE + rekurzivnega queryja
--    (starš, stari starš, prastari starš, ...).
WITH RECURSIVE predniki AS (
    SELECT o.id AS oseba_id,
           rel.stars AS prednik_id,
           1 AS globina,
           o.ime || ' -> ' || relo.ime AS pot
    FROM oseba o
    JOIN otroci rel ON rel.otrok = o.id
    join oseba relo on relo.id = rel.stars

    UNION ALL

    SELECT p.oseba_id,
           rel.stars AS prednik_id,
           p.globina + 1 AS globina,
           p.pot || ' -> ' || relo.ime AS pot
    FROM predniki p
    
    JOIN otroci rel ON rel.otrok = p.prednik_id
    join oseba relo on relo.id = rel.stars
    --WHERE NOT (rel.stars = ANY(p.pot))
)
SELECT o.ime AS oseba,
       pred.ime AS prednik,
       p.pot,
       p.globina
FROM oseba o
LEFT JOIN predniki p ON p.oseba_id = o.id
LEFT JOIN oseba pred ON pred.id = p.prednik_id
ORDER BY o.id, p.globina, pred.ime;


-- =====================
-- GROUP BY, HAVING
-- =====================

-- 5) Za vsako osebo izpiši, koliko otrok ima.
--    Oseb brez otrok ne izpisuj.
SELECT rel.stars AS oseba_id,
       COUNT(*) AS stevilo_otrok
FROM otroci rel
GROUP BY rel.stars;

-- obstajajo tudi druge aggregacijske funkcije
SELECT rel.stars AS oseba_id,
       JSON_AGG(rel.otrok) AS otroci
FROM otroci rel
GROUP BY rel.stars;

-- 6) Za vsako znamko izpiši število traktorjev (vključno z znamkami brez traktorjev).
SELECT z.ime AS znamka,
       COUNT(t.id) AS stevilo_traktorjev
FROM znamka z
LEFT JOIN traktor t ON t.znamka = z.id
GROUP BY z.ime
ORDER BY z.ime;

-- 7) Za vsako neprevidno osebo izpiši, koliko rezervnih delov ima.
--    Neprevidna: ima največ en rezervni del. Vključi tudi osebe brez delov.
SELECT o.id, o.ime,
       COALESCE(SUM(d.stevilo), 0) AS stevilo_delov
FROM oseba o
LEFT JOIN deli d ON d.lastnik = o.id
GROUP BY o.id, o.ime
HAVING COALESCE(sum(d.stevilo), 0) <= 1
ORDER BY o.ime;

-- 8) Izpiši ime osebe z največ vozniškimi izkušnjami.
--    15 minut vožnje na dan za vsak traktor od dneva nakupa do danes.
SELECT o.ime
FROM oseba o
LEFT JOIN traktor t ON t.lastnik = o.id
GROUP BY o.id, o.ime
ORDER BY COALESCE(SUM((CURRENT_DATE - t.nakup) * 15.0 / 60.0), 0) DESC
LIMIT 1;

-- 9) Za vsak tip rezervnega dela izpiši,
--    koliko različnih traktorjev lahko preskrbijo s tem tipom.
SELECT d.tip,
       COUNT(DISTINCT t.id) AS stevilo_traktorjev
FROM deli d
JOIN traktor t ON t.znamka = d.znamka
GROUP BY d.tip
ORDER BY d.tip;

-- 10) V obliki "dan. mesec." izpiši datume,
--     na katere imata rojstni dan vsaj dve osebi.
SELECT (EXTRACT(DAY FROM o.rojstvo)::INT || '. ' || EXTRACT(MONTH FROM o.rojstvo)::INT || '.') AS datum
FROM oseba o
GROUP BY EXTRACT(MONTH FROM o.rojstvo), EXTRACT(DAY FROM o.rojstvo)
HAVING COUNT(*) >= 2
ORDER BY EXTRACT(MONTH FROM o.rojstvo), EXTRACT(DAY FROM o.rojstvo);
