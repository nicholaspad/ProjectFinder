from datetime import datetime

from dotenv import load_dotenv
import pytz

from emails import *
from models import *
from utils import *

load_dotenv()
EMAIL_PW = os.environ["EMAIL_PW"]
BATCH_SIZE = 50

"""
These two methods are designed to be run once a day at 9am.
"""


def send_overdue_email(test_email=None):
    header = f"Subject: {OVERDUE_SUBJECT}\n\n"
    message = header + OVERDUE_MESSAGE
    to = []

    if test_email:
        send_email(
            [test_email],
            message,
            EMAIL_PW,
        )
        return

    due_date = Config.objects.first().due_date
    diff = datetime.now(tz=pytz.timezone("US/Eastern")) - due_date
    if diff.days != 0:
        return

    users = User.objects.filter(~Q(username="admin"), entry__isnull=True)
    for user in users:
        if user.email:
            to.append(user.email)
            continue
        netid = user.username.split("-")[-1]
        to.append(f"{netid}@princeton.edu")

    for i in range(0, len(to), BATCH_SIZE):
        send_email(
            to[i : i + BATCH_SIZE],
            message,
            EMAIL_PW,
        )

    log_email(users, "overdue")


def send_reminder_email(test_email=None):
    header = f"Subject: {REMINDER_SUBJECT}\n\n"
    message = header + REMINDER_MESSAGE
    to = []

    if test_email:
        send_email(
            [test_email],
            message,
            EMAIL_PW,
        )
        return

    due_date = Config.objects.first().due_date
    diff = due_date - datetime.now(tz=pytz.timezone("US/Eastern"))
    if diff.days != 1:
        return

    users = User.objects.filter(~Q(username="admin"))
    for user in users:
        if user.email:
            to.append(user.email)
            continue
        netid = user.username.split("-")[-1]
        to.append(f"{netid}@princeton.edu")

    for i in range(0, len(to), BATCH_SIZE):
        send_email(
            to[i : i + BATCH_SIZE],
            message,
            EMAIL_PW,
        )

    log_email(users, "reminder")
