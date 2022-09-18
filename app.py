import re

from flask import Flask, Response, render_template, request
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


@app.route("/", methods=["GET"])
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


@app.route("/update-settings", methods=["POST"])
def update_settings():
    netid = CASClient().authenticate()
    user = User.query.filter(User.netid == netid).first()
    if user is None:
        return Response(status=400)

    email = request.form.get("email")
    first_name = request.form.get("firstName")
    last_name = request.form.get("lastName")

    if (
        not re.match(r"[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,4}$", email)
        or len(first_name) < 1
        or len(last_name) < 1
    ):
        return Response(status=400)

    user.email = email
    user.first_name = first_name
    user.last_name = last_name

    db.commit()
    return Response(status=201)


@app.route("/logout")
def logout():
    CASClient().logout()
