from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .helper import DBHelperMixin
from . import db, int_pk, fk_user, fk_game, fk_team, User, Game, GameStatus, Team

class Pick(DBHelperMixin, db.Model):
    """A user's pick to win a game."""
    __tablename__ = 'picks'

    id: Mapped[int_pk]
    user_id: Mapped[fk_user]
    game_id: Mapped[fk_game]
    team_id: Mapped[fk_team]
    # create_date: Mapped[datetime] = mapped_column(default=datetime.now())
    # update_date: Mapped[datetime] = mapped_column(default=datetime.now())

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
        return f"<Pick #{self.id}: {self.user.username} picked {self.team.name} for Game #{self.game_id}>"

    @property
    def is_correct(self):
        return self.game.winning_team and self.team.id == self.game.winning_team.id

    def as_dict(self):
        return {
            'id': self.id,
            'userID': self.user_id,
            'gameID': self.game_id,
            'teamID': self.team_id,
            'correct': self.is_correct
        }
