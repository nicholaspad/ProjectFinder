from datetime import datetime
import sys

from dotenv import load_dotenv
import pytz
import sqlalchemy as sa

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
        print(f"Sending test overdue email to {test_email}")
        send_email(
            [test_email],
            message,
            EMAIL_PW,
        )
        return

    config = Config.query.first()
    due_date = timezone("US/Eastern").localize(config.due_date)
    diff = datetime.now(tz=pytz.timezone("US/Eastern")) - due_date
    if diff.days != 0:
        print("Skipped sending overdue emails")
        return

    print("Sending overdue emails")

    users = db.query(User).filter(User.entry == sa.null())
    for user in users:
        to.append(user.email)

    for i in range(0, len(to), BATCH_SIZE):
        batch_to = to[i : i + BATCH_SIZE]
        print(f"Emailing {batch_to}")
        send_email(
            batch_to,
            message,
            EMAIL_PW,
        )

    log_email(users, "overdue")
    print("Sent overdue emails")


def send_reminder_email(test_email=None):
    header = f"Subject: {REMINDER_SUBJECT}\n\n"
    message = header + REMINDER_MESSAGE
    to = []

    if test_email:
        print(f"Sending test reminder email to {test_email}")
        send_email(
            [test_email],
            message,
            EMAIL_PW,
        )
        return

    config = Config.query.first()
    due_date = timezone("US/Eastern").localize(config.due_date)
    diff = due_date - datetime.now(tz=pytz.timezone("US/Eastern"))
    if diff.days != 1:
        print("Skipped sending reminder emails")
        return

    print("Sending reminder emails")

    users = User.query.all()
    for user in users:
        to.append(user.email)

    for i in range(0, len(to), BATCH_SIZE):
        batch_to = to[i : i + BATCH_SIZE]
        print(f"Emailing {batch_to}")
        send_email(
            batch_to,
            message,
            EMAIL_PW,
        )

    log_email(users, "reminder")
    print("Send reminder emails")


if __name__ == "__main__":
    # Add a test email address after python cron.py
    # $ python cron.py nicholaspad@princeton.edu
    test_email_address = sys.argv[1] if len(sys.argv) == 2 else None

    send_reminder_email(test_email_address)
    send_overdue_email(test_email_address)
