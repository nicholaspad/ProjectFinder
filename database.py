import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

load_dotenv()
if os.environ["PROD"] == "1":
    DATABASE_URL = os.environ["DATABASE_URL"]
    # must start with postgresql:// instead of postgres://
    engine = create_engine(DATABASE_URL[:8] + "ql" + DATABASE_URL[8:])
else:
    engine = create_engine("sqlite:///test.db")
db = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base = declarative_base()
Base.query = db.query_property()


def init_db():
    import models

    Base.metadata.create_all(bind=engine)
