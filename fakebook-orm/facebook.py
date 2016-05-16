import datetime
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

# osnova vseh tabel
Base = declarative_base()

class Uporabnik(Base):
    """Uporabnik v sistemu."""
    __tablename__ = 'uporabnik'   # definicija imena tabele
    username = Column(String, primary_key=True)  # enolicno uporabnisko ime
    password = Column(String) # geslo
    ime = Column(String) # polno ime uporabnika

    # Relacija preko vezne tabele Prijatelji
    mojiPrijatelji = relationship("Uporabnik",
                                  secondary="prijatelj",
                                  primaryjoin="Uporabnik.username==Prijatelj.uporabnik1",
                                  secondaryjoin="Uporabnik.username==Prijatelj.uporabnik2",
                                  backref="prijateljiZMenoj")

class Trac(Base):
    """Tema, ki jo komentiramo (Trac)"""
    __tablename__ = 'trac'
    id = Column(Integer, primary_key=True, autoincrement=True) 
    avtor_id = Column(String, ForeignKey('uporabnik.username')) # povezava na avtorja
    avtor = relationship(Uporabnik, backref=backref('traci', uselist=True))
    cas = Column(DateTime, default=datetime.datetime.utcnow) # avtomaticno generiran cas odprtja traca
    vsebina = Column(String)

    def komentiraj(self, avtor, vsebina):
        """Ustvari komentar danega avtorja z dano vsebino ob casu klica."""
        c = Komentar(vsebina = vsebina)
        c.avtor = avtor
        c.trac = self
        return c


class Komentar(Base):
    """Komentar danega avtorja k temi (Tracu)."""
    __tablename__ = 'komentar'
    id = Column(Integer, primary_key=True, autoincrement=True) # ! autoincrement!!!
    vsebina = Column(String)  # vsebina komentarja
    trac_id = Column(Integer, ForeignKey('trac.id')) # povezava na trac
    trac = relationship(Trac, backref=backref('komentarji', uselist=True))
    avtor_id = Column(String, ForeignKey('uporabnik.username')) # povezava na avtorja
    avtor = relationship(Uporabnik, backref=backref('komentarji', uselist=True))
    cas = Column(DateTime, default=datetime.datetime.utcnow)# avtomaticno generiran cas komentiranja

                   
class Prijatelj(Base):
    """Povezovalna tabela ki doloca kdo je prijatelj s kom"""
    __tablename__ = 'prijatelj'
    id = Column(Integer, primary_key=True, autoincrement=True)
    # uporabnik1 zeli/hoce/je prijatelj z uporabnikom 2
    uporabnik1 = Column(String, ForeignKey('uporabnik.username'))   
    uporabnik2 = Column(String, ForeignKey('uporabnik.username'))



                                  

                                


