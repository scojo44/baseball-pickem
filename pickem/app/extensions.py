from datetime import date
from flask_debugtoolbar import DebugToolbarExtension
from flask_bcrypt import Bcrypt
from flask_apscheduler import APScheduler
from werkzeug.routing import BaseConverter

class DateConverter(BaseConverter):
    def to_python(self, value):
        try:
            day = date.fromisoformat(value)
        except ValueError:
            day = date.today()
        return day

    def to_url(self, day: date|str):
        if isinstance(day, str):
            return day
        else:
            return day.isoformat()

debug_toolbar = DebugToolbarExtension()
bcrypt = Bcrypt()
scheduler = APScheduler()
