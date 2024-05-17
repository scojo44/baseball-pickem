"""Models for the Pickem app."""
from datetime import datetime, timezone
from typing import Annotated
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, registry, mapped_column

# Shortcuts for common columns
int_pk = Annotated[int, mapped_column(primary_key=True, autoincrement=True)]
int_api_id = Annotated[int, mapped_column(unique=True)]
timestamp = Annotated[datetime, mapped_column(default=datetime.now(timezone.utc))]
# Foreign Keys
fk_user = Annotated[int, mapped_column(ForeignKey("users.id"))]
fk_sport = Annotated[int, mapped_column(ForeignKey("sports.id"))]
fk_season = Annotated[int, mapped_column(ForeignKey("seasons.id"))]
fk_subseason = Annotated[int, mapped_column(ForeignKey("subseasons.id"))]
fk_league = Annotated[int, mapped_column(ForeignKey("leagues.id"))]
fk_team = Annotated[int, mapped_column(ForeignKey("teams.id"))]
fk_game = Annotated[int, mapped_column(ForeignKey("games.id"))]
# Aliases for length-limited strings
str20 = Annotated[str, 20]
str50 = Annotated[str, 50]
str_bcrypt_hash = Annotated[str, 60]
str_email = Annotated[str, 254] # Longest email address allowed in an SMTP transaction

class Base(DeclarativeBase):
    registry = registry(
        type_annotation_map={
            str20: String(20),
            str50: String(50),
            str_email: String(254),
            str_bcrypt_hash: String(60)
        }
    )

db = SQLAlchemy(model_class=Base)

from .user import User
from .sport import Sport
from .season import Season
from .subseason import SubSeason, SubSeasonType
from .league import League
from .team import Team
from .game import Game, GameStatus
from .pick import Pick
