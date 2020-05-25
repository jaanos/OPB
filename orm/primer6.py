import os
 
from sqlalchemy import Column, DateTime, String, Integer, ForeignKey, func
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Oddelek(Base):
    __tablename__ = 'oddelek'
    id = Column(Integer, primary_key=True)
    naziv = Column(String)
    seznamZaposlenih = relationship(
        'Zaposleni',   # Ime razreda lahko podamo kot niz (ker še ni definirano)
        secondary='povezava'
    )
    def __repr__(self):
        return "Oddelek[{0}, {1}]".format(self.id, self.naziv)

 
class Zaposleni(Base):
    __tablename__ = 'zaposleni'
    id = Column(Integer, primary_key=True)
    ime = Column(String)
    datum_zaposlitve = Column(DateTime, default=func.now())
    oddelki = relationship(
        Oddelek,
        secondary='povezava'
    )
    def __repr__(self):
        return "Zaposleni[{0}, {1}, {2}]".format(self.id, self.ime, self.datum_zaposlitve)    

 
 
class Povezava(Base):
    __tablename__ = 'povezava'
    oddelek_id = Column(Integer, ForeignKey('oddelek.id'), primary_key=True)
    zaposelni_id = Column(Integer, ForeignKey('zaposleni.id'), primary_key=True)

baza = 'baza3.db'
# Izbris baze (datoteke)
if os.path.exists(baza):
    os.remove(baza)

engine = create_engine('sqlite:///{0}'.format(baza), echo=True)

# Ustvarjanje tabel
Base.metadata.create_all(engine)
 
DBSessionMaker = sessionmaker(bind=engine)
session = DBSessionMaker()

input("\nUstvarimo dva oddelka in 3 zaposlene.")
IT = Oddelek(naziv="IT")
finance = Oddelek(naziv="finance")
metka = Zaposleni(ime="Metka")
janez = Zaposleni(ime="Janez")
katka = Zaposleni(ime="Katka")

katka.oddelki.append(finance)
finance.seznamZaposlenih.append(metka)
janez.oddelki.append(IT)
session.add(IT)
session.add(finance)
session.add(janez)
session.add(metka)
session.add(katka)
session.commit()

input("\nJanezovi oddelki: {0}".format(
    janez.oddelki
))
input("\nZaposleni na oddelku Finance: {0}".format(
    finance.seznamZaposlenih
))
input("\nZaposleni na oddelku Finance (s poizvedbo): {0}".format(
    session.query(Oddelek).filter(Oddelek.naziv == 'finance').one().seznamZaposlenih
))
input("\nZaposleni na oddelku Finance (s poizvedbo z druge strani): {0}".format(
    session.query(Zaposleni).filter(Zaposleni.oddelki.any(Oddelek.naziv == 'finance')).all()
))
