from flask import Flask, render_template
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

    entries = Entry.query.all()
    table_data = [
        {
            "name": f"{entry.user.first_name} {entry.user.last_name}",
            "netid": entry.user.netid,
            "skills": entry.skills.split(", "),
            "interests": entry.interests,
            "project_name": entry.project_name,
            "project_description": entry.project_description,
        }
        for entry in entries
    ]

    context = {
        "user": user,
        "config": Config.query.first(),
        "user_entry": user.entry,
        "has_completed_settings": (
            user and user.email and user.first_name and user.last_name
        ),
        "has_created_entry": user.entry is not None,
        "table_data": table_data,
    }

    return render_template("index.html", **context)


@app.route("/logout")
def logout():
    CASClient().logout()
