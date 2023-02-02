# knjižnico sqlalchemy namestimo z
# python -m pip install sqlalchemy
# oz. če nimamo administratorskih pravic
# python -m pip install --user sqlalchemy
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
 
Base = declarative_base()
 
class Oseba(Base):
    # Tako se bo imenavala tabela v bazi
    __tablename__ = 'oseba'
    # Atributi (lastnosti), ki sledijo se preslikajo v stolpce
    id = Column(Integer, primary_key=True)  # Primarni ključ
    ime = Column(String(250), nullable=False) # Ne sme biti null
 
class Naslov(Base):
    __tablename__ = 'naslov'
    id = Column(Integer, primary_key=True)
    ulica = Column(String(250))
    hisna_stevilka = Column(String(250))
    postna_stevilka = Column(String(250), nullable=False)
    oseba_id = Column(Integer, ForeignKey('oseba.id')) # tuji ključ
    # Lastnost, ki odraža povezavo do tabele oseba. 
    # Ker je enolično določena, ne rabimo dodatnih parametrov
    oseba = relationship(Oseba)
 
# Klic grenerira podatkovno bazo v sqlite (datoteko baza.db) oz
# se poveže z njo, če datoteka že obstaja.
# Če želimo izpise SQL stavkov, nastavimo echo=True. Tega v produkciji NE nastavimo.
engine = create_engine('sqlite:///baza.db', echo=True)

# Poveži 'engine' na razred 'Base'
Base.metadata.bind = engine

# POZOR: tabele še niso ustvarjene na bazi. Glej primer2.py