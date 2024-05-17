from flask import Blueprint

UNSAVED_PICKS_KEY = 'Game Picks Session Key'
bp = Blueprint("picks", __name__, url_prefix="/picks")

from . import routes
