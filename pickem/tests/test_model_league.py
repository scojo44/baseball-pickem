"""League model tests."""
from app.models import League
from .base import PickemTestCase

class LeagueModelTestCase(PickemTestCase):
    """League Model Tests."""
    def test_constructor(self):
        """Test the basic model."""
        with self.app.app_context():
            league = League.get(1)
            self.assertEqual(league.name, "Major League Baseball")
            self.assertEqual(league.abbreviation, "MLB")
            self.assertEqual(league.api_id, 1)
            self.assertEqual(league.sport_id, 1)
            # Test relationships
            self.assertEqual(league.sport.id, 1)
            self.assertEqual(len(league.seasons), 1)
            self.assertEqual(len(league.teams), 32)

    def test_repr(self):
        """Test the __repr__ method."""
        with self.app.app_context():
            league = League.get(1)
            self.assertEqual(f"{league}", f"<League #{league.id}: Major League Baseball>")
