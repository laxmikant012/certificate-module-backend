from sqlalchemy import Integer, String, Date, Column, DateTime
import datetime
from database.database import Base


class UploadDetails(Base):
    __tablename__ = "details"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(40))
    completion_date = Column(Date)
    issued_by = Column(String(50))
    designation = Column(String(30))
    email = Column(String(40))
    created_on = Column(DateTime, default=datetime.datetime.utcnow())


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(40))
    email = Column(String(40))
    password = Column(String(40))
