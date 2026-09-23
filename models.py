from database import Base
from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey


class Users(Base):

    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String,unique=True)
    email = Column(String, unique=True)
    hash_password = Column(String)
    role = Column(String, default="user")


class Transactions(Base):

    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    amount = Column(Float)
    type = Column(String)
    category = Column(String)
    date = Column(Date)
    owner_id = Column(Integer, ForeignKey("users.id"))