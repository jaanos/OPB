# http://www.pythoncentral.io/sqlalchemy-orm-examples/
from sqlalchemy import Column, DateTime, String, Integer, ForeignKey, func
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
 
 
Base = declarative_base()
 
 
class Department(Base):
    __tablename__ = 'department'
    id = Column(Integer, primary_key=True)
    name = Column(String)
 
 
class Employee(Base):
    __tablename__ = 'employee'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    # Use default=func.now() to set the default hiring time
    # of an Employee to be the current time when an
    # Employee record was created
    hired_on = Column(DateTime, default=func.now())
    department_id = Column(Integer, ForeignKey('department.id'))
    # Use cascade='delete,all' to propagate the deletion of a Department onto its Employees
    department = relationship(
        Department,
        backref=backref('employees',
                         uselist=True,
                         cascade='delete,all'))
 
 
from sqlalchemy import create_engine
engine = create_engine('sqlite:///orm_in_detail.sqlite', echo=True)
 
from sqlalchemy.orm import sessionmaker
session = sessionmaker()
session.configure(bind=engine)
Base.metadata.create_all(engine)


##>>> d = Department(name="IT")
##>>> emp1 = Employee(name="John", department=d)
##>>> s = session()
##>>> s.add(d)
##>>> s.add(emp1)
##>>> s.commit()
##>>> s.delete(d)  # Deleting the department also deletes all of its employees.
##>>> s.commit()
##>>> s.query(Employee).all()
##
##>>> emp2 = Employee(name="Marry")                                                                                                                  
##>>> emp2.hired_on
##>>> s.add(emp2)
##>>> emp2.hired_on
##>>> s.commit()
##>>> emp2.hired_on
##
##>>> print func.now()
##>>> from sqlalchemy import select
##>>> rs = s.execute(select([func.now()]))
##>>> rs.fetchone()
##
##>>> for department in s.query(Department).all():
##...     s.delete(department)
##...
##>>> s.commit()
##>>> s.query(Department).count()
##0
##>>> s.query(Employee).count()
##0
##
##IT = Department(name="IT")
##Financial = Department(name="Financial")
##john = Employee(name="John", department=IT)
##marry = Employee(name="marry", department=Financial)
##s.add(IT)
##s.add(Financial)
##s.add(john)
##s.add(marry)
##s.commit()
##cathy = Employee(name="Cathy", department=Financial)
##s.add(cathy)
##s.commit()
##
##>>>s.query(Employee).filter(Employee.name.startswith("C")).one().name
##>>> s.query(Employee).join(Employee.department).filter(Employee.name.startswith('C'), Department.name == 'Financial').all()[0].name
##>>> from datetime import datetime
### Find all employees who will be hired in the future
##>>> s.query(Employee).filter(Employee.hired_on > func.now()).count()
##0
### Find all employees who have been hired in the past
##>>> s.query(Employee).filter(Employee.hired_on < func.now()).count()
##3
def test():
    d = Department(name="IT")
    emp1 = Employee(name="John", department=d)
    s = session()
    s.add(d)
    s.add(emp1)
    s.commit()
    s.delete(d)  # Deleting the department also deletes all of its employees.
    s.commit()
    s.query(Employee).all()

    emp2 = Employee(name="Marry")                                                                                                                  
    emp2.hired_on
    s.add(emp2)
    emp2.hired_on
    s.commit()
    emp2.hired_on

    print(func.now())

    from sqlalchemy import select
    rs = s.execute(select([func.now()]))
    rs.fetchone()

    for department in s.query(Department).all():
        s.delete(department)

    s.commit()
    s.query(Department).count()

    IT = Department(name="IT")
    Financial = Department(name="Financial")
    john = Employee(name="John", department=IT)
    marry = Employee(name="marry", department=Financial)
    s.add(IT)
    s.add(Financial)
    s.add(john)
    s.add(marry)
    s.commit()
    cathy = Employee(name="Cathy", department=Financial)
    s.add(cathy)
    s.commit()
    s.query(Employee).count()
        
    s.query(Employee).filter(Employee.name.startswith("C")).one().name

    s.query(Employee).join(Employee.department).filter(Employee.name.startswith('C'), Department.name == 'Financial').all()[0].name    
