"""The League model."""
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .helper import DBHelperMixin
from . import db, int_pk, int_api_id, fk_sport, str20, str50

class League(DBHelperMixin, db.Model):
    """An organization managing a group of teams competing in a certain sport (NFL, MLB, FIFA, etc)."""
    __tablename__ = 'leagues'

    id: Mapped[int_pk]
    api_id: Mapped[int_api_id]
    name: Mapped[str50]
    abbreviation: Mapped[str20]
    sport_id: Mapped[fk_sport]

    # "One" side of one-to-many relationships
    sport: Mapped["Sport"] = relationship(back_populates='leagues')

    # "Many" side of one-to-many relationships
    seasons: Mapped[list['Season']] = relationship(back_populates='league')
    teams: Mapped[list['Team']] = relationship(back_populates='league')

    @classmethod
    def create_from_espn(cls, league: dict, sport_id: int):
        """Create a League object from the ESPN API."""
        return cls(league['name'], league['abbreviation'], league['id'], sport_id)

    def __init__(self, name: str, abbr: str, api_id: int, sport_id: int):
        """Create a League object."""
        self.name = name
        self.api_id = api_id
        self.abbreviation = abbr
        self.sport_id = sport_id

    def __repr__(self):
        """String representation of a league."""
        return f"<League #{self.id}: {self.name}>"
