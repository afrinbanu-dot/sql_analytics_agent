from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from connection import Base
import datetime

class Account(Base):
    __tablename__ = "accounts"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    industry = Column(String)
    annual_revenue = Column(Float)
    region = Column(String)
    
    opportunities = relationship("Opportunity", back_populates="account")
    contacts = relationship("Contact", back_populates="account")

class Contact(Base):
    __tablename__ = "contacts"
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    title = Column(String)
    account_id = Column(Integer, ForeignKey("accounts.id"))
    
    account = relationship("Account", back_populates="contacts")

class Opportunity(Base):
    __tablename__ = "opportunities"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    stage = Column(String, nullable=False) # e.g., Prospecting, Qualification, Proposal, Closed Won, Closed Lost
    close_date = Column(DateTime)
    account_id = Column(Integer, ForeignKey("accounts.id"))
    
    account = relationship("Account", back_populates="opportunities")
    interactions = relationship("Interaction", back_populates="opportunity")

class Interaction(Base):
    __tablename__ = "interactions"
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, nullable=False) # e.g., Email, Call, Meeting
    notes = Column(Text)
    date = Column(DateTime, default=datetime.datetime.utcnow)
    opportunity_id = Column(Integer, ForeignKey("opportunities.id"))
    
    opportunity = relationship("Opportunity", back_populates="interactions")

# --- HR / Employee Data Models ---

class Department(Base):
    __tablename__ = "departments"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    budget = Column(Float)
    
    employees = relationship("Employee", back_populates="department")

class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    role = Column(String)
    salary = Column(Float)
    hire_date = Column(DateTime, default=datetime.datetime.utcnow)
    department_id = Column(Integer, ForeignKey("departments.id"))
    
    department = relationship("Department", back_populates="employees")
    time_off = relationship("TimeOff", back_populates="employee")

class TimeOff(Base):
    __tablename__ = "time_off"
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    type = Column(String, nullable=False) # Vacation, Sick, Parental
    days = Column(Integer, nullable=False)
    status = Column(String, nullable=False, default="Pending") # Approved, Pending, Rejected
    
    employee = relationship("Employee", back_populates="time_off")
