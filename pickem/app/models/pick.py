"""The Pick model."""
from datetime import datetime, timezone
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import DateTime
from .helper import DBHelperMixin
from . import db, int_pk, fk_user, fk_game, fk_team, User, Game, GameStatus, Team

class Pick(DBHelperMixin, db.Model):
    """A user's pick to win a game."""
    __tablename__ = 'picks'

    id: Mapped[int_pk]
    user_id: Mapped[fk_user]
    game_id: Mapped[fk_game]
    team_id: Mapped[fk_team]
    create_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    update_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now(timezone.utc))

    # "One" side of one-to-many relationships
    user: Mapped[User] = relationship(back_populates='picks')
    game: Mapped[Game] = relationship()
    team: Mapped[Team] = relationship()

    def __init__(self, user: int, game: int, team: int):
        """Create a Pick object."""
        self.user_id = user
        self.game_id = game
        self.team_id = team

    def __repr__(self):
        """String representation of a pick."""
        return f"<Pick #{self.id}: {self.user.username} picked {self.team.name} for Game #{self.game_id}>"

    @property
    def is_correct(self):
        """Returns true if the user picked the team that won the game."""
        return self.game.winning_team and self.team.id == self.game.winning_team.id

    def as_dict(self):
        """Returns a dictionary version of the pick."""
        return {
            'id': self.id,
            'userID': self.user_id,
            'gameID': self.game_id,
            'teamID': self.team_id,
            'correct': self.is_correct
        }
