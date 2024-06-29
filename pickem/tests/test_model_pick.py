"""Pick model tests."""
from app.models import Pick
from .base import PickemTestCase

class PickModelTestCase(PickemTestCase):
    """Pick Model Tests."""
    def test_constructor(self):
        """Test the basic model."""
        with self.app.app_context():
            pick = Pick.get(self.mario_pick_id)
            self.assertEqual(pick.user_id, self.mario_id)
            self.assertEqual(pick.game_id, 171)
            self.assertEqual(pick.team_id, 28)
            # Test relationships
            self.assertEqual(pick.user.id, self.mario_id)
            self.assertEqual(pick.user.username, "mario")
            self.assertEqual(pick.game.id, 171)
            self.assertEqual(pick.game.home_score, 9)
            self.assertEqual(pick.team.id, 28)
            self.assertEqual(pick.team.name, "Rangers")

    def test_repr(self):
        """Test the __repr__ method."""
        with self.app.app_context():
            pick = Pick.get(self.mario_pick_id)
            self.assertEqual(f"{pick}", f"<Pick #{pick.id}: mario picked Rangers for Game #171>")

    def test_is_correct(self):
        """Test the is_correct property for a correct pick."""
        with self.app.app_context():
            # Correct pick
            pick = Pick.get(self.mario_pick_id)
            self.assertTrue(pick.is_correct)
            # Incorrect pick
            pick = Pick.get(self.luigi_pick_id)
            self.assertFalse(pick.is_correct)

    def test_as_dict(self):
        """Test the as_dict method."""
        with self.app.app_context():
            pick = Pick.get(self.mario_pick_id)
            self.assertDictEqual(pick.as_dict(), {
                'id': self.mario_pick_id,
                'userID': self.mario_id,
                'gameID': 171,
                'teamID': 28,
                'correct': True
            }
)
