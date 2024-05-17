from flask import Blueprint

UNSAVED_PICKS_KEY = 'Game Picks Session Key'
bp = Blueprint("games", __name__)

from . import routes
