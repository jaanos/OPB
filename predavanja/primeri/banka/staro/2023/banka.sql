DROP TABLE IF EXISTS kraj;
DROP TABLE IF EXISTS oseba;
DROP TABLE IF EXISTS racun;
DROP TABLE IF EXISTS transakcija;

CREATE TABLE kraj (
    posta      INTEGER  PRIMARY KEY,
    kraj       TEXT     NOT NULL
);

CREATE TABLE oseba (
    ime        TEXT     NOT NULL,
    priimek    TEXT     NOT NULL,
    emso       TEXT     PRIMARY KEY,
    naslov     TEXT     NOT NULL,
    posta_id   INTEGER  REFERENCES kraj(posta) 
);

CREATE TABLE racun (
    racun      INTEGER  PRIMARY KEY AUTOINCREMENT,
    lastnik_id TEXT     REFERENCES oseba(emso)
);

CREATE TABLE transakcija (
    id         INTEGER  PRIMARY KEY AUTOINCREMENT,
    racun_id   INTEGER  REFERENCES racun(racun),
    znesek     DECIMAL  NOT NULL,
    datum      DATETIME NOT NULL DEFAULT (datetime('now')) 
);
