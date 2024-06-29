"""Season model tests."""
from app.models import Season
from .base import PickemTestCase

class SeasonModelTestCase(PickemTestCase):
    """Season Model Tests."""
    def test_constructor(self):
        """Test the basic model."""
        with self.app.app_context():
            season = Season.get(1)
            self.assertEqual(season.name, "2024")
            self.assertEqual(season.year, 2024)
            self.assertEqual(season.league_id, 1)
            # Test relationships
            self.assertEqual(season.league.id, 1)
            self.assertEqual(len(season.subseasons), 1)

    def test_repr(self):
        """Test the __repr__ method."""
        with self.app.app_context():
            season = Season.get(1)
            self.assertEqual(f"{season}", f"<Season #{season.id}: 2024 [2024]>")

    def test_full_name(self):
        """Test the full_name property."""
        with self.app.app_context():
            season = Season.get(1)
            self.assertEqual(season.full_name, "2024 Major League Baseball Season")
