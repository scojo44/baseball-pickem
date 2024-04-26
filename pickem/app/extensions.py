from flask_debugtoolbar import DebugToolbarExtension
from flask_bcrypt import Bcrypt
from flask_apscheduler import APScheduler

debug_toolbar = DebugToolbarExtension()
bcrypt = Bcrypt()
scheduler = APScheduler()
