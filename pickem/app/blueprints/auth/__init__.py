from flask import Blueprint

CURRENT_USER_KEY = "User Logged In Session Key"
bp = Blueprint("auth", __name__)

from . import routes
