from sqlalchemy.orm import Mapped, relationship
from .helper import DBHelperMixin
from . import db, int_pk, fk_league, str50

class Season(DBHelperMixin, db.Model):
    """A full season of organized competition in a particular league (ex. the 2023-2024 NFL Football season)."""
    __tablename__ = 'seasons'

    id: Mapped[int_pk]
    name: Mapped[str50]
    year: Mapped[int] # The year commonly associated with the season (2023 in the above example)
    league_id: Mapped[fk_league]

    # "One" side of one-to-many relationships
    league: Mapped["League"] = relationship(back_populates='seasons')

    # "Many" side of one-to-many relationships
    subseasons: Mapped[list['SubSeason']] = relationship(back_populates='season', cascade='all')

    def __init__(self, name: str, year: int, league_id: int):
        """Create a Season object."""
        self.name = name
        self.year = year
        self.league_id = league_id

    def __repr__(self):
        return f"<Season #{self.id}: {self.name} [{self.year}]>"

    @property
    def full_name(self):
        """Returns the team location and name (ex., Seattle Mariners)."""
        return f"{self.name} {self.league.name} Season"
