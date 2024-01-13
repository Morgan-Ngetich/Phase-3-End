from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Association table for the many-to-many relationship between Employee and Project
employee_project_association = Table(
    'employee_project_association',
    Base.metadata,
    Column('employee_id', Integer, ForeignKey('employees.id')),
    Column('project_id', Integer, ForeignKey('projects.id'))
)

class Department(Base):
    __tablename__ = 'departments'
    id = Column(Integer, primary_key=True)
    name = Column(String)  # Update the column name to 'name'
    head_of_department_id = Column(Integer, ForeignKey('employees.id'))
    head_of_department = relationship('Employee', foreign_keys=[head_of_department_id], uselist=False)
    employees = relationship('Employee', backref='department', foreign_keys='Employee.department_id')
    projects = relationship('Project', back_populates='department')



class Employee(Base):
    __tablename__ = 'employees'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    department_id = Column(Integer, ForeignKey('departments.id'))
    projects = relationship('Project', secondary=employee_project_association, back_populates='employees')

class Project(Base):
    __tablename__ = 'projects'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    department_id = Column(Integer, ForeignKey('departments.id'))
    department = relationship('Department', back_populates='projects')
    employees = relationship('Employee', secondary=employee_project_association, back_populates='projects')
