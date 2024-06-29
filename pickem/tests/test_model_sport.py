"""Sport model tests."""
from app.models import Sport
from .base import PickemTestCase

class SportModelTestCase(PickemTestCase):
    """Sport Model Tests."""
    def test_constructor(self):
        """Test the basic model."""
        with self.app.app_context():
            sport = Sport.get(1)
            self.assertEqual(sport.name, "Baseball")

    def test_repr(self):
        """Test the __repr__ method."""
        with self.app.app_context():
            sport = Sport.get(1)
            self.assertEqual(f"{sport}", f"<Sport #{sport.id}: Baseball>")
