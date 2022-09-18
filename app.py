from flask import Flask
from pytz import timezone

from CASClient import CASClient
from database import db

app = Flask(__name__)
app.config["TIMEZONE"] = timezone("US/Eastern")


@app.teardown_appcontext
def shutdown_session(exception=None):
    db.remove()


@app.route("/")
def index():
    netid = CASClient().authenticate()
    return netid


@app.route("/logout")
def logout():
    CASClient().logout()
