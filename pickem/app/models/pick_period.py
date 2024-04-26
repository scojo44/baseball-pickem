from datetime import datetime
from sqlalchemy.orm import Mapped
from .helper import DBHelperMixin
from . import db, int_pk

class PickPeriod(DBHelperMixin, db.Model):
    """A time period with games for users to pick a winner (day, week, etc)."""
    __tablename__ = 'pick_periods'

    id: Mapped[int_pk]
    start: Mapped[datetime]
    end: Mapped[datetime]

    def __repr__(self):
        return f"<PickPeriod #{self.id}: {self.start} {self.end}>"
