from datetime import datetime

from flask_admin.contrib.sqla import ModelView
from pytz import timezone
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from CASClient import CASClient
from database import Base


class AdminView(ModelView):
    def is_accessible(self):
        netid = CASClient().authenticate()
        return User.query.filter(User.netid == netid).first().is_admin


class AdminViewRestricted(AdminView):
    can_create = False
    can_delete = False


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    netid = Column(String(20), unique=True, nullable=False)
    first_name = Column(String(50), default="", unique=False, nullable=True)
    last_name = Column(String(50), default="", unique=False, nullable=True)
    email = Column(String(50), default="", unique=True)
    entry = relationship("Entry", backref="user", uselist=False)
    email_log = relationship("EmailLog", backref="user")
    is_admin = Column(Boolean, default=False, unique=False, nullable=True)

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

    def __repr__(self):
        netid = self.user.netid if self.user else "Unknown"
        return f"<Entry user={netid!r} project_name={self.project_name!r}>"


class EmailLog(Base):
    __tablename__ = "email_logs"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    date = Column(
        DateTime, nullable=False, default=datetime.now(tz=timezone("US/Eastern"))
    )
    email_type = Column(String(100), nullable=False)

    def __repr__(self):
        netid = self.user.netid if self.user else "Unknown"
        return f"<EmailLog user={netid!r} email_type={self.email_type!r}>"
