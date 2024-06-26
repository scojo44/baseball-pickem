"""The Sport model."""
from sqlalchemy.orm import Mapped, relationship
from .helper import DBHelperMixin
from . import db, int_pk, int_api_id, str20

class Sport(DBHelperMixin, db.Model):
    """A sport played at a game."""
    __tablename__ = 'sports'

    id: Mapped[int_pk]
    # api_id: Mapped[int_api_id]
    name: Mapped[str20]

    # "Many" side of one-to-many relationships
    leagues: Mapped[list['League']] = relationship(back_populates='sport')

    @classmethod
    def create_from_espn(cls, sport: dict):
        """Create a Sport object from the ESPN API."""
        return cls(sport['name'], sport['id'])

    def __init__(self, name: str, api_id: int = None):
        """Create a Sport object."""
        self.api_id = api_id
        self.name = name

    def __repr__(self):
        """String representation of a sport."""
        return f"<Sport #{self.id}: {self.name}>"
