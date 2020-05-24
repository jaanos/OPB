from primer1 import Oseba, Naslov, Base, engine
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DBSessionMaker = sessionmaker(bind=engine)
session = DBSessionMaker()

# Izvedi poizvedbo "SELECT * FROM oseba"
print(session.query(Oseba).all())

# Vrni prvo Osebo in jo izpiši
oseba1 = session.query(Oseba).first()
print(oseba1)
print("IME:", oseba1.ime)

# Poišči vse naslove od osebe 'oseba1' in jih izpiši kot objekte
print(session.query(Naslov).filter(Naslov.oseba == oseba1).all())

# Poišči en tak naslov in ga vrni ter izpiši
naslov1 = session.query(Naslov).filter(Naslov.oseba == oseba1).one()
print(naslov1)
print(naslov1.postna_stevilka)
