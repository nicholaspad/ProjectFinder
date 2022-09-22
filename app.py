import os
import re

from dotenv import load_dotenv
from flask import Flask, Response, render_template, request
from flask_admin import Admin
from flask_admin.menu import MenuLink
from flask_migrate import Migrate
from pytz import timezone

from CASClient import CASClient
from database import db
from models import *
from utils import *

load_dotenv()
app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]
app.config["TIMEZONE"] = timezone("US/Eastern")
app.config["FLASK_ADMIN_SWATCH"] = "cerulean"

admin = Admin(app, name="ProjectFinder", template_mode="bootstrap4")
admin.add_view(AdminView(User, db))
admin.add_view(AdminViewRestricted(Config, db))
admin.add_view(AdminView(Entry, db))
admin.add_view(AdminViewRestricted(EmailLog, db))

admin.add_link(MenuLink(name="Live Website", category="", url="/"))

Migrate(app, db)


@app.teardown_appcontext
def shutdown_session(exception=None):
    db.remove()


@app.route("/landing", methods=["GET"])
def landing():
    return render_template("landing.html")


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
        "is_past_due": is_past_due(),
        "is_admin": user.netid in AdminView.ADMIN_NETIDS,
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
        or not first_name
        or not last_name
    ):
        return Response(status=400)

    user.email = email
    user.first_name = first_name
    user.last_name = last_name

    db.commit()
    return Response(status=201)


@app.route("/create-or-update-entry", methods=["POST"])
def create_or_update_entry():
    netid = CASClient().authenticate()
    user = User.query.filter(User.netid == netid).first()
    if user is None:
        return Response(status=400)

    skills = request.form.get("skills")
    interests = request.form.get("interests")
    project_name = request.form.get("projectName")
    project_description = request.form.get("projectDescription")

    if not skills or not interests or is_past_due():
        return Response(status=400)

    entry = user.entry if user.entry else Entry()
    entry.skills = ", ".join(filter(None, [e.strip() for e in skills.split(",")]))
    entry.interests = interests.strip()
    entry.project_name = project_name.strip()
    entry.project_description = project_description.strip()

    if user.entry is None:
        entry.user_id = user.id
        db.add(entry)

    db.commit()
    return Response(status=201)


@app.route("/delete-entry", methods=["POST"])
def delete_entry():
    netid = CASClient().authenticate()
    user = User.query.filter(User.netid == netid).first()
    if user is None:
        return Response(status=400)

    if user.entry is None:
        return Response(status=201)

    db.delete(user.entry)

    db.commit()
    return Response(status=201)


@app.route("/logout")
def logout():
    CASClient().logout()
