"""Blueprint for game pages."""
from flask import Blueprint

UNSAVED_PICKS_KEY = 'Game Picks Session Key'
bp = Blueprint("game", __name__)

from . import routes
