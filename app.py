from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from pytz import timezone

from CASClient import CASClient

app = Flask(__name__)
app.secret_key = b"insecure-key"
app.config["TIMEZONE"] = timezone("US/Eastern")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.sqlite"
db = SQLAlchemy(app)


from models import *  # noqa


@app.route("/")
def index():
    netid = CASClient().authenticate()
    return netid


@app.route("/logout")
def logout():
    CASClient().logout()
