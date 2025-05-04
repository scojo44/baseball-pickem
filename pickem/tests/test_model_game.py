"""Game model tests."""
from app.models import db, Game, GameStatus
from .base import PickemTestCase

class GameModelTestCase(PickemTestCase):
    """Game Model Tests."""
    def test_constructor(self):
        """Test the basic model."""
        with self.app.app_context():
            game = Game.get(self.mario_pick_game_id)
            self.assertEqual(game.away_team_id, 14)
            self.assertEqual(game.home_team_id, 25)
            self.assertEqual(game.away_score, 3)
            self.assertEqual(game.home_score, 9)
            self.assertEqual(game.status, GameStatus.Final)
            self.assertEqual(game.api_id, 401695364)
            self.assertEqual(game.subseason_id, 1)
            # Test relationships
            self.assertEqual(game.subseason.id, 1)
            self.assertEqual(game.away_team.id, 14)
            self.assertEqual(game.home_team.id, 25)

    def test_repr(self):
        """Test the __repr__ method."""
        with self.app.app_context():
            game = Game.get(self.mario_pick_game_id)
            self.assertEqual(f"{game}", f"<Game #{game.id}: Angels @ Mariners, 2025-04-30 1:10 PM>")

    def test_can_have_score(self):
        """Test the can_have_score property."""
        with self.app.app_context():
            game = Game.get(self.mario_pick_game_id)
            self.assertTrue(game.can_have_score)

    def test_is_over(self):
        """Test the is_over property."""
        with self.app.app_context():
            game = Game.get(self.mario_pick_game_id)
            self.assertTrue(game.is_over)

    def test_winning_team(self):
        """Test the winning_team property."""
        with self.app.app_context():
            game = Game.get(self.mario_pick_game_id)
            self.assertEqual(game.winning_team.id, 25)
            self.assertEqual(game.winning_team.name, "Mariners")

    def test_start_time_display(self):
        """Test the start_time_display property."""
        with self.app.app_context():
            game = Game.get(self.mario_pick_game_id)
            self.assertEqual(game.start_time_display, "1:10 PM")

    def test_display_stat(self):
        """Test the display_stat method."""
        with self.app.app_context():
            game = Game.get_first(db.select(Game).where(Game.status == GameStatus.Scheduled)) # Not started yet
            self.assertEqual(game.display_stat(None), "-")
            game = Game.get_first(db.select(Game).where(Game.status == GameStatus.InProgress)) # Started, and in progress
            self.assertEqual(game.display_stat(None), 0)
            game = Game.get_first(db.select(Game).where(Game.status == GameStatus.Final)) # Started, and finished with a winner
            self.assertEqual(game.display_stat(5), 5)
            self.assertEqual(game.display_stat(None), 0)
            game = Game.get_first(db.select(Game).where(Game.status == GameStatus.RainDelay)) # Started, but delayed by rain
            self.assertEqual(game.display_stat(None), 0)
            game = Game.get_first(db.select(Game).where(Game.status == GameStatus.Delayed)) # Started, but delayed for some other reason
            self.assertEqual(game.display_stat(None), 0)
            # game = Game.get_first(db.select(Game).where(Game.status == GameStatus.Postponed)) # Started, but postponed before becoming an official game (5+ innings played)
            # self.assertEqual(game.display_stat(None), "-")
            game = Game.get_first(db.select(Game).where(Game.status == GameStatus.Canceled)) # Cancelled before scheduled time
            self.assertEqual(game.display_stat(None), "-")

    def test_as_dict(self):
        """Test the as_dict method."""
        with self.app.app_context():
            game = Game.get(self.mario_pick_game_id)
            self.maxDiff = None # Show all differences in output
            self.assertDictEqual(game.as_dict(), {
                'id': self.mario_pick_game_id,
                'apiID': 401695364,
                'startTime': "2025-04-30T13:10:00-07:00",
                'status': "Final",
                'statusDetail': "Final",
                'subseasonID': 1,
                'winTeamID': 25,
                'awayTeam': {
                    'id': 14,
                    'apiID': 3,
                    'name': "Angels",
                    'location': "Los Angeles",
                    'abbreviation': "LAA",
                    'logoURL': "https://a.espncdn.com/i/teamlogos/mlb/500/laa.png",
                    'leagueID': 1,
                    'score': 3,
                    'hits': 10,
                    'errors': 2
                },
                'homeTeam': {
                    'id': 25,
                    'apiID': 12,
                    'name': "Mariners",
                    'location': "Seattle",
                    'abbreviation': "SEA",
                    'logoURL': "https://a.espncdn.com/i/teamlogos/mlb/500/sea.png",
                    'leagueID': 1,
                    'score': 9,
                    'hits': 12,
                    'errors': 1
                }
            }
)
