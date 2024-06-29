"""Team model tests."""
from app.models import db, Team
from .base import PickemTestCase

class TeamModelTestCase(PickemTestCase):
    """Team Model Tests."""
    def test_constructor(self):
        """Test the basic model."""
        with self.app.app_context():
            team = Team.get(25)
            self.assertEqual(team.name, "Mariners")
            self.assertEqual(team.location, "Seattle")
            self.assertEqual(team.abbreviation, "SEA")
            self.assertEqual(team.api_id, 32)
            self.assertEqual(team.league_id, 1)
            self.assertEqual(team.logo_url, "https://a.espncdn.com/i/teamlogos/mlb/500/sea.png")
            # Test relationships
            self.assertEqual(team.league.id, 1)

    def test_repr(self):
        """Test the __repr__ method."""
        with self.app.app_context():
            team = Team.get(25)
            self.assertEqual(f"{team}", f"<Team #{team.id}: Seattle Mariners>")

    def test_full_name(self):
        """Test the full_name property."""
        with self.app.app_context():
            team = Team.get(25)
            self.assertEqual(team.full_name, "Seattle Mariners")

    def test_as_dict(self):
        """Test the as_dict method."""
        with self.app.app_context():
            team = Team.get(25)
            self.assertDictEqual(team.as_dict(), {
                'id': team.id,
                'apiID': 32,
                'name': "Mariners",
                'location': "Seattle",
                'abbreviation': "SEA",
                'logoURL': "https://a.espncdn.com/i/teamlogos/mlb/500/sea.png",
                'leagueID': 1
            }
)
