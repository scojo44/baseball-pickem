"""Picks blueprint tests."""
# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database
import os
os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

# Now we can import app
from unittest import TestCase
from app import create_app
from app.models import db, User
from app.blueprints.auth import CURRENT_USER_KEY
from app.blueprints.picks import UNSAVED_PICKS_KEY

app = create_app()
app.testing = True

# Don't have WTForms use CSRF at all, since it's a pain to test
app.config['WTF_CSRF_ENABLED'] = False
app.config["TESTING"] = True # Have Flask return real errors w/o HTML
app.config["DEBUG_TB_HOSTS"] = ["dont-show-debug-toolbar"]

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data
with app.app_context():
    db.create_all()

class PicksBlueprintTestCase(TestCase):
    """Test views for the picks blueprint."""

    def setUp(self):
        """Create test client, add sample data."""
        with app.app_context():
            [db.session.delete(user) for user in User.get_all()]
            db.session.commit()

            mario = User.signup(username="mario", password="99coins")
            luigi = User.signup(username="luigi", password="mansion5")
            db.session.commit()

            self.mario_id = mario.id
            self.luigi_id = luigi.id

    def tearDown(self):
        """Clear any incomplete transactions."""
        with app.app_context():
            db.session.rollback()

    # Helper functions
    def login_user(self, http, user_id=None):
        """Helper function to log in a user."""
        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:
        with http.session_transaction() as sess:
            sess[CURRENT_USER_KEY] = user_id or self.mario_id

    def is_get_route_as_anon_blocked(self, route):
        """Check that the route blocks anon users."""
        with app.test_client() as http:
            resp = http.get(route, follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", html)
            self.assertIn("Username", html) # Redirected to login page
            self.assertIn("Password", html)
            self.assertIn("Log in", html)

    def is_post_route_as_anon_blocked(self, route, post_data={}):
        """Check that posting to the route blocks anon users."""
        with app.test_client() as http:
            resp = http.post(route, data=post_data, follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", html)

    def missing_item_returns_404(self, route):
        """Check that the route returns a 404 error for missing items."""
        with app.test_client() as http:
            self.login_user(http)
            resp = http.get(route)
            self.assertEqual(resp.status_code, 404)

    # Picks API Tests
    def test_add_pick(self):
        """Can the user add a pick?"""
        for n in range(1, 1000):
            with app.test_client() as http:
                self.login_user(http)
                post_data = {"game_id":"123", "team_id":"789"}
                resp = http.post("/picks/add", data=post_data)
                json = resp.get_json()
                self.assertEqual(resp.status_code, 200)
                self.assertDictEqual({'result': True}, json)
                with http.session_transaction() as sess:
                    picks = sess.get(UNSAVED_PICKS_KEY)
                self.assertEqual(len(picks), 1)
                self.assertDictEqual(picks[0], {'123': '789'})
