from flask import Flask
from flask import render_template
from pytz import timezone

from CASClient import CASClient
from database import db
from models import *

app = Flask(__name__)
app.config["SECRET_KEY"] = "abcdefg1234567"
app.config["TIMEZONE"] = timezone("US/Eastern")


@app.teardown_appcontext
def shutdown_session(exception=None):
    db.remove()


@app.route("/")
def index():
    netid = CASClient().authenticate()
    user = User.query.filter(User.netid == netid).first()
    if user is None:
        user = User(netid)
        db.add(user)
        db.commit()

    context = {"user": user}

    return render_template("index.html", **context)


@app.route("/logout")
def logout():
    CASClient().logout()
