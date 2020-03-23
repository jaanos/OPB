DROP TABLE IF EXISTS posta;
DROP TABLE IF EXISTS oseba;
DROP TABLE IF EXISTS racun;
DROP TABLE IF EXISTS transakcija;

CREATE TABLE posta (
    postna_st INTEGER PRIMARY KEY,
    posta     CHAR    NOT NULL
);

CREATE TABLE oseba (
    ime            CHAR    NOT NULL,
    priimek        CHAR    NOT NULL,
    emso           CHAR    PRIMARY KEY,
    ulica          CHAR    NOT NULL,
    hisna_stevilka CHAR    NOT NULL,
    posta_id       INTEGER REFERENCES posta (postna_st) 
);

CREATE TABLE racun (
    lastnik_id  CHAR    REFERENCES oseba (emso),
    racun INTEGER PRIMARY KEY AUTOINCREMENT
);

CREATE TABLE transakcija (
    id     INTEGER  PRIMARY KEY AUTOINCREMENT,
    racun_id  INTEGER  REFERENCES racun(racun),
    znesek DECIMAL  NOT NULL,
    datum  DATETIME NOT NULL DEFAULT (datetime('now') ) 
);

