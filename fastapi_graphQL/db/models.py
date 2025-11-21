#model.py
from sqlalchemy import Column, Integer, String
from db.database import Base

class EmployeeModel(Base):
    __tablename__ = 'tbl_employees'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=False)
    job = Column(String(100), nullable=False)
    language = Column(String(100), nullable=False)
    pay = Column(Integer, nullable=False)