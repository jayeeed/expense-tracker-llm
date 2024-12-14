from sqlalchemy import Column, Integer, String
from .database import Base


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(String, index=True)
    category = Column(String, index=True)
    amount = Column(Integer, index=True)
    description = Column(String, index=True)
