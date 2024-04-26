from sqlalchemy.orm import Mapped, relationship
from .helper import DBHelperMixin
from . import db, int_pk, fk_game, fk_team, fk_pick_sheet

class Pick(DBHelperMixin, db.Model):
    """A user's pick to win a game."""
    __tablename__ = 'picks'

    id: Mapped[int_pk]
    game_id: Mapped[fk_game]
    picked_team_id: Mapped[fk_team]
    pick_sheet_id: Mapped[fk_pick_sheet]

    # "One" side of one-to-many relationships
    pick_sheet: Mapped["PickSheet"] = relationship(back_populates='picks')

    def __repr__(self):
        return f"<Pick #{self.id}: Picked Team #{self.picked_team_id} PickSheet #{self.pick_sheet_id}>"
