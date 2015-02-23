--- VERZIJA ZA SQLite ---

----------------------------------------------------------------------
-- banka
-- poenostavljeno poslovanje v banki
----------------------------------------------------------------------

----------------------------------------------------------------------
-- tabela krajev s postnimi stevilkami 
----------------------------------------------------------------------
CREATE TABLE kraj (
  posta		INTEGER PRIMARY KEY,
  kraj		TEXT
);

----------------------------------------------------------------------
-- tabela fizicnih oseb, ki so lastniki racunov
----------------------------------------------------------------------

CREATE TABLE oseba (
  emso		TEXT PRIMARY KEY,
  ime		TEXT,
  priimek	TEXT,
  rojstvo	DATE,
  ulica		TEXT,
  posta		INTEGER,
  CONSTRAINT oseba_1 FOREIGN KEY (posta) REFERENCES kraj(posta)
);


----------------------------------------------------------------------
-- tabela racunov
----------------------------------------------------------------------

CREATE TABLE racun (
  stevilka      INTEGER PRIMARY KEY AUTOINCREMENT,
  lastnik       TEXT NOT NULL,
  CONSTRAINT racun_1 FOREIGN KEY (lastnik) REFERENCES oseba(emso)
);

----------------------------------------------------------------------
-- tabela vseh transakcij (pologov in dvigov denarja)
----------------------------------------------------------------------

CREATE TABLE transakcija (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  znesek        INTEGER NOT NULL,
  racun         INTEGER NOT NULL,
  cas           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  opis          TEXT,
  CONSTRAINT transakcija_1 FOREIGN KEY (racun) REFERENCES racun(stevilka)
);



