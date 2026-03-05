-- 1) Ustvarimo tabelo oseba

create table oseba(
    id INTEGER PRIMARY KEY,
    ime text not null,
    rojstvo date not null
);

select * from oseba;

-- Če želimo popravit kakšno napako imamo načeloma več opcij:
-- 1. popravimo tabelo: to naredimo z pomočjo ukaza alter table
-- 2. pobrišemo tabelo in jo naredimo znova: to naredimo z drop table ukazom

-- DROP table oseba;

-- Sedaj lahko tabelo naredimo znova.

-- 2) Ustvarimo tabelo otroci
CREATE table otroci(
    stars integer references oseba(id), -- referenciramo se na tabelo oseba
    otrok integer references oseba(id),
    PRIMARY KEY(stars, otrok), -- nastavimo primarni ključ - to zahetva,
    -- da je kombicija (stars, otrok) enolična. Torej ni podvojitev.
    CHECK(stars <> otrok) -- preverimo, da oseba ne more biti sama sebi starš
)

-- Otrok je obvezen podatek!
-- insert into otroci values(1, null);

-- 3) Ustvarimo tabelo znamka
CREATE table znamka(
    id SERIAL PRIMARY KEY, -- SERIAL je zelo uporabna oznaka.
    -- Avtomatsko ustvari števec (začetek v 1) ter naredi stolpec tipa integer.
    ime text UNIQUE NOT NULL
);

-- 4) Ustvarimo tabelo traktor
-- Ustvarimo tabelo traktor
create table traktor(
    id serial primary key,
    lastnik integer  references oseba(id),
    znamka integer references znamka(id),
    barva text,
    nakup date not null default now() check(nakup <= now())
    -- za nakup povemo, da je tipa date, ne sme biti prazen, privzeta vrednost je trenutni datum,
    -- zahtevamo pa, da datum nakupa ni v prihodnosti
);

-- 5) Ustvarimo tabelo deli
create table deli(
    lastnik integer not null references oseba(id),
    znamka integer not null references znamka(id),
    tip text not null,
    stevilo integer not null default 1 check(stevilo > -1)
    -- podobno kot prej: tip integer, ne sme biti prazen, privzeta vrednost je 1,
    -- zahteva, da je stevilo delov pozitivno
);

