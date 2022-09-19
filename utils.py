import pytz

from models import *


def is_past_due():
    config = Config.query.first()
    return timezone("US/Eastern").localize(config.due_date) < datetime.now(
        tz=pytz.timezone("US/Eastern")
    )
