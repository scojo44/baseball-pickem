"""The Game model and GameStatus enumeration."""
from enum import StrEnum
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import DateTime
from .helper import DBHelperMixin
from . import db, int_pk, int_api_id, fk_subseason, fk_team

class GameStatus(StrEnum):
    """The status of a scheduled game."""
    NS = 'Not Started'
    IN1 = '1st'
    IN2 = '2nd'
    IN3 = '3rd'
    IN4 = '4th'
    IN5 = '5th'
    IN6 = '6th'
    IN7 = '7th'
    IN8 = '8th'
    IN9 = '9th'
    INTR = 'Delay'
    POST = 'Postponed'
    ABD = 'Abandoned'
    CANC = 'Canceled'
    FT = 'Final'

class Game(DBHelperMixin, db.Model):
    """A game for users to try to guess the winner."""
    __tablename__ = 'games'

    id: Mapped[int_pk]
    api_id: Mapped[int_api_id]
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    status: Mapped[GameStatus] = mapped_column(default=GameStatus.NS)
    # To store enum values in database: values_callable=lambda gs: [m.value for m in gs]), 
    home_team_id: Mapped[fk_team]
    away_team_id: Mapped[fk_team]
    home_score: Mapped[Optional[int]]
    away_score: Mapped[Optional[int]]
    home_hits: Mapped[Optional[int]]
    away_hits: Mapped[Optional[int]]
    home_errors: Mapped[Optional[int]]
    away_errors: Mapped[Optional[int]]
    subseason_id: Mapped[fk_subseason]

    # "One" side of one-to-many relationships
    subseason: Mapped["SubSeason"] = relationship(back_populates='games')
    home_team: Mapped["Team"] = relationship(foreign_keys='Game.home_team_id')
    away_team: Mapped["Team"] = relationship(foreign_keys='Game.away_team_id')

    @classmethod
    def create_from_espn(cls, team: dict, league_id: int):
        """Create a Game object from the ESPN API."""
        return cls(team['name'], team['abbreviation'], team['location'], team['id'], league_id)

    def __init__(self, start: datetime, away_team_id: int, home_team_id: int, api_id: int, subseason_id: int, status: GameStatus = GameStatus.NS, away_score: int = None, home_score: int = None, away_hits: int = None, home_hits: int = None, away_errors: int = None, home_errors: int = None):
        """Create a Game object."""
        # Store times as Pacific time so games are filed under the correct date on My Picks and the Scoreboard
        self.start_time = start
        self.away_team_id = away_team_id
        self.home_team_id = home_team_id
        self.status = status
        self.away_score = away_score
        self.home_score = home_score
        self.away_hits = away_hits
        self.home_hits = home_hits
        self.away_errors = away_errors
        self.home_errors = home_errors
        self.api_id = api_id
        self.subseason_id = subseason_id

    def __repr__(self):
        """String representation of a game."""
        return f"<Game #{self.id}: {self.away_team.name} @ {self.home_team.name}, {self.start_time.date()} {self.start_time_display}>"

    @property
    def can_have_score(self):
        """Returns true if the game is in progress, finished or abandoned."""
        return self.status not in [GameStatus.NS, GameStatus.POST, GameStatus.CANC]

    @property
    def is_over(self):
        """Returns true if the game has been played."""
        return self.status == GameStatus.FT
    
    @property
    def winning_team(self):
        """Returns the ID of the winning team."""
        away_won = self.is_over and self.away_score > self.home_score
        home_won = self.is_over and self.away_score < self.home_score
        win_team = self.away_team if away_won else self.home_team if home_won else None
        return win_team

    @property
    def start_time_display(self):
        """A displayable version so the game's start time."""
        return self.start_time.strftime('%-I:%M %p')

    def display_stat(self, stat: int|None):
        """Returns the stat if the game is in progress or finished or '-' if the game hasn't started or was cancelled."""
        if stat is None:
            return 0 if self.can_have_score else '-'
        else:
            return stat

    def as_dict(self):
        """Returns a dictionary version of the game."""
        return {
            'id': self.id,
            'apiID': self.api_id,
            'startTime': self.start_time.isoformat(),
            'status': str(self.status),
            'subseasonID': self.subseason_id,
            'winTeamID': self.winning_team.id if self.winning_team else None,
            'awayTeam': {
                **self.away_team.as_dict(),
                'score': self.display_stat(self.away_score),
                'hits': self.display_stat(self.away_hits),
                'errors': self.display_stat(self.away_errors)
            },
            'homeTeam': {
                **self.home_team.as_dict(),
                'score': self.display_stat(self.home_score),
                'hits': self.display_stat(self.home_hits),
                'errors': self.display_stat(self.home_errors)
            }
        }
