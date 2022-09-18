from flask import Flask
from flask import render_template
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from pytz import timezone

from CASClient import CASClient
from database import db
from models import *

app = Flask(__name__)
app.config["SECRET_KEY"] = "abcdefg1234567"
app.config["TIMEZONE"] = timezone("US/Eastern")
app.config["FLASK_ADMIN_SWATCH"] = "cerulean"

admin = Admin(app, name="ProjectFinder", template_mode="bootstrap4")
admin.add_view(ModelView(User, db))
admin.add_view(ModelView(Config, db))
admin.add_view(ModelView(Entry, db))


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
