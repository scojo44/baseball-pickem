"""Subseason model tests."""
from app.models.subseason import SubSeason, SubSeasonType
from .base import PickemTestCase

class SubseasonModelTestCase(PickemTestCase):
    """Subseason Model Tests."""
    def test_constructor(self):
        """Test the basic model."""
        with self.app.app_context():
            subseason = SubSeason.get(1)
            self.assertEqual(subseason.name, "Regular Season")
            self.assertEqual(subseason.type, SubSeasonType.regular)
            self.assertEqual(subseason.season_id, 1)
            # Test relationships
            self.assertEqual(subseason.season.id, 1)
            self.assertEqual(len(subseason.games), 2682)

    def test_repr(self):
        """Test the __repr__ method."""
        with self.app.app_context():
            subseason = SubSeason.get(1)
            self.assertEqual(f"{subseason}", f"<SubSeason #{subseason.id}: 2024 Regular Season>")
