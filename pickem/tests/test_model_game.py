"""Game model tests."""
from app.models import Game, GameStatus
from .base import PickemTestCase

class GameModelTestCase(PickemTestCase):
    """Game Model Tests."""
    def test_constructor(self):
        """Test the basic model."""
        with self.app.app_context():
            game = Game.get(171)
            self.assertEqual(game.away_team_id, 28)
            self.assertEqual(game.home_team_id, 25)
            self.assertEqual(game.away_score, 10)
            self.assertEqual(game.home_score, 9)
            self.assertEqual(game.status, GameStatus.FT)
            self.assertEqual(game.api_id, 152923)
            self.assertEqual(game.subseason_id, 1)
            # Test relationships
            self.assertEqual(game.subseason.id, 1)
            self.assertEqual(game.home_team.id, 25)
            self.assertEqual(game.away_team.id, 28)

    def test_repr(self):
        """Test the __repr__ method."""
        with self.app.app_context():
            game = Game.get(171)
            self.assertEqual(f"{game}", f"<Game #{game.id}: Rangers @ Mariners, 2024-03-05 12:10 PM>")

    def test_can_have_score(self):
        """Test the can_have_score property."""
        with self.app.app_context():
            game = Game.get(171)
            self.assertTrue(game.can_have_score)

    def test_is_over(self):
        """Test the is_over property."""
        with self.app.app_context():
            game = Game.get(171)
            self.assertTrue(game.is_over)

    def test_winning_team(self):
        """Test the winning_team property."""
        with self.app.app_context():
            game = Game.get(171)
            self.assertEqual(game.winning_team.id, 28)
            self.assertEqual(game.winning_team.name, "Rangers")

    def test_start_time_display(self):
        """Test the start_time_display property."""
        with self.app.app_context():
            game = Game.get(171)
            self.assertEqual(game.start_time_display, "12:10 PM")

    def test_display_stat(self):
        """Test the display_stat method."""
        with self.app.app_context():
            game = Game.get(171) # A game that has been played
            self.assertEqual(game.display_stat(5), 5)
            self.assertEqual(game.display_stat(None), 0)
            game = Game.get(1160) # A game that has started but not finished
            self.assertEqual(game.display_stat(None), 0)
            game = Game.get(313) # A game that was postponed
            self.assertEqual(game.display_stat(None), "-")
            game = Game.get(315) # A game that was cancelled
            self.assertEqual(game.display_stat(None), "-")
            game = Game.get(2682) # A game that hasn't started
            self.assertEqual(game.display_stat(None), "-")

    def test_as_dict(self):
        """Test the as_dict method."""
        with self.app.app_context():
            game = Game.get(171)
            self.maxDiff = None # Show all differences in output
            self.assertDictEqual(game.as_dict(), {
                'id': 171,
                'apiID': 152923,
                'startTime': "2024-03-05T12:10:00-08:00",
                'status': "Final",
                'subseasonID': 1,
                'winTeamID': 28,
                'awayTeam': {
                    'id': 28,
                    'apiID': 35,
                    'name': "Rangers",
                    'location': "Texas",
                    'abbreviation': "TEX",
                    'logoURL': "https://a.espncdn.com/i/teamlogos/mlb/500/tex.png",
                    'leagueID': 1,
                    'score': 10,
                    'hits': 12,
                    'errors': 3
                },
                'homeTeam': {
                    'id': 25,
                    'apiID': 32,
                    'name': "Mariners",
                    'location': "Seattle",
                    'abbreviation': "SEA",
                    'logoURL': "https://a.espncdn.com/i/teamlogos/mlb/500/sea.png",
                    'leagueID': 1,
                    'score': 9,
                    'hits': 9,
                    'errors': 0
                }
            }
)
