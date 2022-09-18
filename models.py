from datetime import datetime
from email.policy import default

from pytz import timezone
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    netid = Column(String(20), unique=True, nullable=False)
    first_name = Column(String(50), unique=False, nullable=True)
    last_name = Column(String(50), unique=False, nullable=True)
    email = Column(String(50), unique=True)
    entry = relationship("Entry", backref="user", uselist=False)

    def __init__(self, netid):
        self.netid = netid
        self.email = f"{netid}@princeton.edu"

    def __repr__(self):
        return f"<User netid={self.netid!r}>"


class Config(Base):
    __tablename__ = "config"
    id = Column(Integer, primary_key=True)
    due_date = Column(
        DateTime, nullable=False, default=datetime.now(tz=timezone("US/Eastern"))
    )

    def __repr__(self):
        return f"<Config due_date={self.due_date!r}>"


class Entry(Base):
    __tablename__ = "entries"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_date = Column(
        DateTime, nullable=False, default=datetime.now(tz=timezone("US/Eastern"))
    )
    last_modified_date = Column(
        DateTime, nullable=False, default=datetime.now(tz=timezone("US/Eastern"))
    )
    skills = Column(String(500), nullable=False, default="")
    interests = Column(String(500), nullable=False, default="")
    project_name = Column(String(100), nullable=False, default="")
    project_description = Column(String(500), nullable=False, default="")
