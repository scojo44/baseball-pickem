from enum import StrEnum
from datetime import datetime
from typing import Optional
import sqlalchemy as sqla
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .helper import DBHelperMixin
from . import db, int_pk, int_api_id, fk_subseason, fk_team, str20, str50

class GameStatus(StrEnum):
    """The status of a scheduled game."""
    not_started = 'NS'
    inning1 = 'IN1'
    inning2 = 'IN2'
    inning3 = 'IN3'
    inning4 = 'IN4'
    inning5 = 'IN5'
    inning6 = 'IN6'
    inning7 = 'IN7'
    inning8 = 'IN8'
    inning9 = 'IN9'
    interrupted = 'INTR'
    postponed = 'POST'
    abandoned = 'ABD'
    cancelled = 'CANC'
    finished = 'FT'

class Game(DBHelperMixin, db.Model):
    """A game for users to try to guess the winner."""
    __tablename__ = 'games'

    id: Mapped[int_pk]
    api_id: Mapped[int_api_id]
    # name: Mapped[str50]
    # short_name: Mapped[Optional[str20]]
    start_time: Mapped[datetime]
    status: Mapped[GameStatus] = mapped_column(sqla.Enum(GameStatus, values_callable=lambda gs: [m.value for m in gs]), default=GameStatus.not_started)
    home_team_id: Mapped[fk_team]
    away_team_id: Mapped[fk_team]
    home_score: Mapped[Optional[int]]
    away_score: Mapped[Optional[int]]
    subseason_id: Mapped[fk_subseason]

    # "One" side of one-to-many relationships
    subseason: Mapped["SubSeason"] = relationship(back_populates='games')
    home_team: Mapped["Team"] = relationship(foreign_keys='Game.home_team_id')
    away_team: Mapped["Team"] = relationship(foreign_keys='Game.away_team_id')

    @classmethod
    def create_from_espn(cls, team: dict, league_id: int):
        """Create a Game object from the ESPN API."""
        return cls(team['name'], team['abbreviation'], team['location'], team['id'], league_id)

    def __init__(self, start: datetime, home_team_id: int, away_team_id: int, api_id: int, subseason_id: int, status: GameStatus = GameStatus.not_started, home_score: int = None, away_score: int = None):
        """Create a Game object."""
        # self.name = name
        # self.short_name = short_name
        self.start_time = start
        self.home_team_id = home_team_id
        self.away_team_id = away_team_id
        self.status = status
        self.home_score = home_score
        self.away_score = away_score
        self.api_id = api_id
        self.subseason_id = subseason_id

    def __repr__(self):
        return f"<Game #{self.id}: {self.away_team.name} at {self.home_team.name}, {self.start_time}>"
