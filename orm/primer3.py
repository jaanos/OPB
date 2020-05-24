from sqlalchemy import create_engine
from primer1 import Oseba, Naslov, Base, engine
from sqlalchemy.orm import sessionmaker
  
# Odpri generator sej 
DBSessionMaker = sessionmaker(bind=engine)

# Ustvari sejo
session = DBSessionMaker()

# Ustvarimo nov objekt razreda 'Oseba'
nova_oseba = Oseba(ime='Janez')

# Dodamo ga v sejo
session.add(nova_oseba)

# Metoda 'commit' shrani (spremenjene) objekte v seji v podatkovno bazo.
session.commit()
 
# Ustvarimo nov 'Naslov' in ga preko lastnosti 'oseba' povežemo s prej
# ustvarjeno novo osebo.
nov_naslov = Naslov(postna_stevilka='00000', oseba=nova_oseba)
session.add(nov_naslov)
session.commit()
