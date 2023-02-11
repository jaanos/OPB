--- VERZIJA ZA SQLite ---

----------------------------------------------------------------------
-- banka
-- poenostavljeno poslovanje v banki
----------------------------------------------------------------------

----------------------------------------------------------------------
-- tabela krajev s poštnimi številkami 
----------------------------------------------------------------------
CREATE TABLE kraj (
  posta		INTEGER PRIMARY KEY,
  kraj		TEXT NOT NULL
);

----------------------------------------------------------------------
-- tabela fizičnih oseb, ki so lastniki računov
----------------------------------------------------------------------

CREATE TABLE oseba (
  emso    TEXT PRIMARY KEY,
  ime     TEXT NOT NULL,
  priimek TEXT NOT NULL,
  ulica   TEXT NOT NULL,
  posta   INTEGER NOT NULL REFERENCES kraj(posta)
);


----------------------------------------------------------------------
-- tabela računov
----------------------------------------------------------------------

CREATE TABLE racun (
  stevilka INTEGER PRIMARY KEY AUTOINCREMENT,
  lastnik  TEXT NOT NULL REFERENCES oseba(emso)
);

----------------------------------------------------------------------
-- tabela vseh transakcij (pologov in dvigov denarja)
----------------------------------------------------------------------

CREATE TABLE transakcija (
  id     INTEGER PRIMARY KEY AUTOINCREMENT,
  racun  INTEGER NOT NULL REFERENCES racun(stevilka),
  znesek INTEGER NOT NULL, 
  cas    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  opis   TEXT
);
