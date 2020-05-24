from sqlalchemy import Column, DateTime, String, Integer, ForeignKey, func, select
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()
 
class Oddelek(Base):
    __tablename__ = 'oddelek'
    id = Column(Integer, primary_key=True)
    naziv = Column(String)

    def __repr__(self):
        return "Oddelek[{0}, {1}, {2}]".format(self.id, self.naziv, self.seznamZaposlenih)
 
class Zaposleni(Base):
    __tablename__ = 'zaposleni'
    id = Column(Integer, primary_key=True)
    ime = Column(String)
    # uporabimo razred func za dostop do funkcij na bazi, npr. func.now()
    datum_zaposlitve = Column(DateTime, default=func.now())
    oddelek_id = Column(Integer, ForeignKey('oddelek.id'))
    # cascade='delete,all' bo povzročil brisanje vseh zaposlenih v oddelku
    oddelek = relationship(
        Oddelek,
        backref=backref('seznamZaposlenih',
                         uselist=True,
                         cascade='delete,all'))

    def __repr__(self):
        return "Zaposleni[{0}, {1}, {2}, {3}]".format(self.id, self.ime, self.datum_zaposlitve, self.oddelek_id)    
 
 
engine = create_engine('sqlite:///baza2.db', echo=True)
# Ustvarjanje tabel
Base.metadata.create_all(engine)
 
DBSessionMaker = sessionmaker(bind=engine)
session = DBSessionMaker()
    
oddelek1 = Oddelek(naziv="IT")
input("\nUstvarili smo oddelek {0}".format(oddelek1))
zaposleni1 = Zaposleni(ime="Janez", oddelek=oddelek1)
input("\nUstvarili smo zaposlenega {0}".format(zaposleni1))
session.add(oddelek1)
session.add(zaposleni1)
session.commit()
input("\nV bazo smo dodali zaposlenega na oddelku.")
input("\nTrenutna vsebina tabele Zaposleni: {0}".format(
    session.query(Zaposleni).all()
))
input("\nTrenutna vsebina tabele Oddelek: {0}".format(
    session.query(Oddelek).all()
))
input("\nSedaj izbrišimo oddelek1")
session.delete(oddelek1)
session.commit()
input("\nVsebina tabele Zaposleni: {0}".format(
    session.query(Zaposleni).all()
))
input("\nVsebina tabele Oddelek: {0}".format(
    session.query(Oddelek).all()
))

zaposleni2 = Zaposleni(ime="Francka")                                                                                                                  
zaposleni2.datum_zaposlitve
session.add(zaposleni2)
input("\nDatum zaposlitve pred commit: {0}".format(
    zaposleni2.datum_zaposlitve
))
session.commit()
input("\nDatum zaposlitve po commit: {0}".format(zaposleni2.datum_zaposlitve))
input("\nVrednost func.now(): {0}".format(
    func.now()
))

rs = session.execute(select([func.now()]))
input("\nVrednost func.now() po SELECT: {0}".format(
    rs.fetchone()
))
input("\nPobrišemo vse oddelke in uporabnike v njih")
for oddelek in session.query(Oddelek).all():
    session.delete(oddelek)
session.commit()

input("\nVsebina tabele Zaposleni: {0}".format(
    session.query(Zaposleni).all()
))

input("\nUstvarimo dva oddelka in tri zaposlene, ki jih vstavimo v oddelke.")
IT = Oddelek(naziv="IT")
finance = Oddelek(naziv="Finance")
janez = Zaposleni(ime="Janez", oddelek=IT)
metka = Zaposleni(ime="Metka", oddelek=finance)
session.add(IT)
session.add(finance)
session.add(janez)
session.add(metka)
session.commit()
katka = Zaposleni(ime="Katka", oddelek=finance)
session.add(katka)
session.commit()
input("\nŠtevilo zaposlenih je: {0}".format(
    session.query(Zaposleni).count()
))
input("\nIme enega zaposlenega, ki se začne na črko K je: {0}".format(
    session.query(Zaposleni).filter(Zaposleni.ime.startswith("K")).one().ime
))
input("\nIme enega zaposlenega, ki je hkrati v oddelku Finance in se njegovo ime začne na K: {0}".format(
    session.query(Zaposleni).join(Zaposleni.oddelek).filter(Zaposleni.ime.startswith('K'), Oddelek.naziv == 'Finance').all()[0].ime    
))    

input("\nVsi zaposleni, ki so bili zaposleni v preteklosti: {0}".format(
    session.query(Zaposleni).filter(Zaposleni.datum_zaposlitve < func.now()).count()
))
