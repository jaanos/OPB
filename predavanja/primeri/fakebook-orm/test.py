import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from facebook import Base, Uporabnik, Trac, Komentar, Prijatelj
from pomozne import password_md5

### Nastavitve
##IZPISI = True
##BAZA = 'sqlite:///:memory:'   # podatkovna baza v spominu
##
### priklop na podatkovno bazo
##engine = create_engine(BAZA, echo=IZPISI)  
##
### inicializacija generatorja sej
##session = sessionmaker()
##session.configure(bind=engine)

def generiraj(engine, session, test=True):
    # generiranje baze
    Base.metadata.create_all(engine)

    s = session()
        # ustvarimo nekaj uporabnikov
    u1 = Uporabnik(username="Janko", password=password_md5("abc"), ime="Janko Novak")
    u2 = Uporabnik(username="Metka", password=password_md5("def"), ime="Metka Novak")
    u3 = Uporabnik(username="Toncek", password=password_md5("xxx"), ime="Toncek Baloncek")

    #dodamo jih v sejo
    s.add(u1); s.add(u2); s.add(u3)

    #shranimo stanje novih objektov v seji v bazo
    s.commit()

    # usvarimo trac in ga shranimo v bazo
    tr = Trac(vsebina="Cena solate", avtor=u1)
    s.add(tr)
    s.commit()

    # dodajmo nekaj komentarjev
    s.add(tr.komentiraj(u1, vsebina = "Danes je zelena solata po 1.3 EUR"))
    s.add(tr.komentiraj(u2, vsebina = "Ne ni res, se da dobiti po 1.10 EUR."))
    s.add(tr.komentiraj(u1, vsebina = "Ja, imaš prav!!!"))

    s.commit()
    s.close()

    if test:
        s = session()

        # preko poizvedb moramo iz baze v novo sejo pridobiti uporabnike 
        u1 = s.query(Uporabnik).filter(Uporabnik.username == "Janko").one()
        u2, u3 = s.query(Uporabnik).filter(Uporabnik.username != "Janko") # ker vemo, da sta ravno se dva ...

        # izpis komentarjev prvega traca

        trac = u1.traci[0]
        print("Izpis komentarjev na trac: {0}:".format(trac.vsebina))
        for k in trac.komentarji: print("{0}[{1}]:{2}".format(k.avtor.ime, k.cas, k.vsebina))

        # dodajmo prijatelje
        u1.mojiPrijatelji.append(u2)
        u1.mojiPrijatelji.append(u3)
        s.commit()

        # izpis prijateljev
        print("\nPrijatelji od: {0}:".format(u1.ime))
        for p in u1.mojiPrijatelji: print(p.ime)

        # izpis "prijateljev z menoj"
        print("\nKdo misli da je prijatelj z {0}".format(u2.ime))
        for p in u2.prijateljiZMenoj: print(p. ime)

        s.close()

                  

                                


