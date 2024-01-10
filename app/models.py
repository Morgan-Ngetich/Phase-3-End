from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Department(Base):
    __tablename__ = 'departments'
    id = Column(Integer, primary_key=True)
    dept_name = Column(String)
    head_of_dept = Column(Integer, ForeignKey('employees.id'))
    projects = relationship('Project', back_populates='department')
    employees = relationship('Employee', back_populates='department')

class Employee(Base):
    __tablename__ = 'employees'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    department_id = Column(Integer, ForeignKey('departments.id'))
    department = relationship('Department', back_populates='employees')
    projects = relationship('Project', back_populates='employee')

class Project(Base):
    __tablename__ = 'projects'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    employee_id = Column(Integer, ForeignKey('employees.id'))
    employee = relationship('Employee', back_populates='projects')
    department_id = Column(Integer, ForeignKey('departments.id'))
    department = relationship('Department', back_populates='projects')