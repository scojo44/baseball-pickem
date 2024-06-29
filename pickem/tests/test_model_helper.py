"""DBHelper mixin tests."""
from werkzeug.exceptions import NotFound
from app.models import db, Team, Pick
from .base import PickemTestCase

class DBHelperMixinTestCase(PickemTestCase):
    """DBHelperMixin Tests.  All tests have to run with a derived class"""
    def test_get(self):
        """Test the get classmethod."""
        with self.app.app_context():
            team = Team.get(25)
            self.assertEqual(team.id, 25)
            self.assertEqual(team.name, "Mariners")
            self.assertEqual(team.location, "Seattle")

    def test_get_or_404(self):
        """Test the get_or_404 classmethod."""
        with self.app.app_context():
            team = Team.get_or_404(28)
            self.assertEqual(team.id, 28)
            self.assertEqual(team.name, "Rangers")
            self.assertEqual(team.location, "Texas")
            # Team that doesn't exist
            with self.assertRaises(NotFound):
                Team.get_or_404(999)

    def test_get_first(self):
        """Test the get_first classmethod."""
        with self.app.app_context():
            team = Team.get_first(db.select(Team).where(Team.abbreviation == "COL"))
            self.assertEqual(team.id, 9)
            self.assertEqual(team.name, "Rockies")
            self.assertEqual(team.location, "Colorado")
            # Team that doesn't exist
            self.assertIsNone(Team.get_first(db.select(Team).where(Team.name == "xyzzy")))

    def test_get_all(self):
        """Test the get_all classmethod."""
        with self.app.app_context():
            teams = Team.get_all()
            self.assertEqual(len(teams), 32)
            self.assertTrue(isinstance(teams[0], Team))
            # With a filter
            teams = Team.get_all(db.select(Team).where(Team.location == "New York"))
            self.assertEqual(len(teams), 2)
            self.assertTrue(isinstance(teams[0], Team))
            [self.assertEqual(t.location, "New York") for t in teams]
            # No results
            teams = Team.get_all(db.select(Team).where(Team.name == "xyzzy"))
            self.assertEqual(len(teams), 0)

    def test_save(self):
        """Test the save method."""
        with self.app.app_context():
            # Create a pick and try to save it
            pick = Pick(user=self.mario_id, game=373, team=25)
            pick.save()
            # Check that it got an ID
            self.assertTrue(isinstance(pick.id, int))
            # Check that it was saved
            saved_pick = Pick.get(pick.id)
            self.assertEqual(pick.game_id, saved_pick.game_id)
            self.assertEqual(saved_pick.team.name, "Mariners")
            self.assertTrue(saved_pick.is_correct)

    def test_delete(self):
        """Test the delete method."""
        with self.app.app_context():
            pick = Pick.get(self.mario_pick_id)
            pick.delete()
            self.assertIsNone(Pick.get_first(db.select(Pick).where(Pick.id == self.mario_pick_id)))

    def test_get_last_error(self):
        """Test the get_last_error method."""
        with self.app.app_context():
            # Delete a pick
            pick = Pick.get(self.mario_pick_id)
            pick.delete()
            self.assertIsNone(pick.get_last_error())
            # Now saving the deleted pick should throw an exception.  The below line would fix the exception
            # db.make_transient(pick)
            pick.save()
            error = pick.get_last_error()
            self.assertIn("has been deleted.  Use the make_transient() function to send this object back to the transient state.", error)
