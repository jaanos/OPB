--- VERZIJA ZA POSTGRESQL ---

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

-- stevec racunov, se avtomaticno povecuje sam
CREATE SEQUENCE "rstevec" START 100000; 

CREATE TABLE racun (
  stevilka      INTEGER DEFAULT NEXTVAL('rstevec') PRIMARY KEY,
  lastnik       TEXT NOT NULL,
  CONSTRAINT racun_1 FOREIGN KEY (lastnik) REFERENCES oseba(emso)
);


----------------------------------------------------------------------
-- tabela vseh transakcij (pologov in dvigov denarja)
----------------------------------------------------------------------

-- stevec transakcij
CREATE SEQUENCE "tstevec" START 1;

CREATE TABLE transakcija (
  id            INTEGER DEFAULT NEXTVAL('tstevec') PRIMARY KEY,
  znesek        INTEGER NOT NULL,
  racun         INTEGER NOT NULL,
  cas           TIMESTAMP NOT NULL DEFAULT NOW(),
  opis          TEXT,
  CONSTRAINT transakcija_1 FOREIGN KEY (racun) REFERENCES racun(stevilka)
);