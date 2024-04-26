from enum import Enum
from datetime import datetime
from sqlalchemy.orm import Mapped, relationship
from .helper import DBHelperMixin
from . import db, int_pk, fk_season, str50

class SubSeasonType(Enum):
    preseason = 0
    regular = 1
    postseason = 2
    allstar = 3
    exhibition = 4

class SubSeason(DBHelperMixin, db.Model):
    """A portion of a season (preseason, regular, postseason, etc)."""
    __tablename__ = 'subseasons'

    id: Mapped[int_pk]
    name: Mapped[str50]
    season_id: Mapped[fk_season]
    type: Mapped[SubSeasonType]
    start: Mapped[datetime]
    end: Mapped[datetime]

    # "One" side of one-to-many relationships
    season: Mapped["Season"] = relationship(back_populates='subseasons')

    # "Many" side of one-to-many relationships
    games: Mapped[list['Game']] = relationship(back_populates='subseason')

    def __init__(self, name: str, type: SubSeasonType, start: datetime, end: datetime, season_id: int):
        """Create a Season object."""
        self.name = name
        self.type = type
        self.start = start
        self.end = end
        self.season_id = season_id

    def __repr__(self):
        return f"<SubSeason #{self.id}: {self.season.name} {self.name}>"
