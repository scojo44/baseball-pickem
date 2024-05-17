from sqlalchemy.orm import Mapped, relationship
from .helper import DBHelperMixin
from . import db, int_pk, int_api_id, fk_league, str20, str50

class Team(DBHelperMixin, db.Model):
    """A sports team."""
    __tablename__ = 'teams'

    id: Mapped[int_pk]
    api_id: Mapped[int_api_id]
    name: Mapped[str50]
    location: Mapped[str50]
    abbreviation: Mapped[str20]
    logo_url: Mapped[str]
    league_id: Mapped[fk_league]

    # "One" side of one-to-many relationships
    league: Mapped['League'] = relationship(back_populates='teams')

    @classmethod
    def create_from_espn(cls, team: dict, league_id: int):
        """Create a Team object from the ESPN API."""
        return cls(team['name'], team['abbreviation'], team['location'], team['id'], league_id)

    def __init__(self, name: str, location: str, abbr: str, logo_url: str, api_id: int, league_id: int):
        """Create a Team object."""
        self.name = name
        self.location = location
        self.abbreviation = abbr
        self.logo_url = logo_url
        self.api_id = api_id
        self.league_id = league_id

    def __repr__(self):
        return f"<Team #{self.id}: {self.full_name}>"

    @property
    def full_name(self):
        """Returns the team location and name (ex., Seattle Mariners)."""
        if self.location:
            return f"{self.location} {self.name}"
        else:
            return f"{self.name}" # All-Star teams have an empty location field

    def as_dict(self):
        return {
            'id': self.id,
            'apiID': self.api_id,
            'name': self.name,
            'location': self.location,
            'abbreviation': self.abbreviation,
            'logoURL': self.logo_url,
            'leagueID': self.league.id
        }
