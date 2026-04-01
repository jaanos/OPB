from dataclasses import dataclass
from datetime import datetime


@dataclass
class Kraj:
    posta: int
    kraj: str


@dataclass
class Oseba:
    emso: str
    ime: str
    priimek: str
    naslov: str
    kraj: Kraj


@dataclass
class Racun:
    stevilka: int
    lastnik: Oseba


@dataclass
class Transakcija:
    id: int
    racun: Racun
    znesek: int
    cas: datetime = None
    opis: str = None
