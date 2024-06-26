"""Blueprint for user pages."""
from flask import Blueprint

CURRENT_USER_KEY = "User Logged In Session Key"
bp = Blueprint("user", __name__)

from . import routes
