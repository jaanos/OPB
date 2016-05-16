from orm_1 import Person, Base, Address
from sqlalchemy import create_engine
engine = create_engine('sqlite:///sqlalchemy_example.db', echo=True)

Base.metadata.bind = engine
from sqlalchemy.orm import sessionmaker

DBSession = sessionmaker()
DBSession.bind = engine
session = DBSession()

# Make a query to find all Persons in the database
session.query(Person).all()

# Return the first Person from all Persons in the database
person = session.query(Person).first()
print(person.name)

# Find all Address whose person field is pointing to the person object
print(session.query(Address).filter(Address.person == person).all())

# Retrieve one Address whose person field is point to the person object
address = session.query(Address).filter(Address.person == person).one()
print(address.post_code)
