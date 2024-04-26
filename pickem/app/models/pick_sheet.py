from sqlalchemy.orm import Mapped, relationship
from .helper import DBHelperMixin
from . import db, int_pk, fk_user, fk_pick_period

class PickSheet(DBHelperMixin, db.Model):
    """An organization managing a group of teams competing in a certain sport (NFL, MLB, FIFA, etc)."""
    __tablename__ = 'pick_sheets'

    id: Mapped[int_pk]
    user_id: Mapped[fk_user]
    pick_period_id: Mapped[fk_pick_period]

    # "One" side of one-to-many relationships
    user: Mapped["User"] = relationship(back_populates='pick_sheets')

    # "Many" side of one-to-many relationships
    picks: Mapped[list['Pick']] = relationship(back_populates='pick_sheet', cascade='all')

    def __repr__(self):
        return f"<PickSheet #{self.id}: {self.user.username} PickPeriod #{self.pick_period_id}>"
