from unittest import TestCase
from app import create_app
from app.models import db, User
from app.bp_user import CURRENT_USER_KEY

class PickemTestCase(TestCase):
    """Base class for Pickem app tests."""

    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)

        # Create the pickem app for testing using a test configuration
        self.app = create_app(config_filename='config_test')
        self.app.testing = True

        # Create the database tables
        with self.app.app_context():
            db.create_all()

    def setUp(self):
        """Create test client, add sample data."""
        with self.app.app_context():
            [db.session.delete(user) for user in User.get_all()]
            db.session.commit()

            mario = User.signup(username="mario", password="99coins")
            luigi = User.signup(username="luigi", password="mansion5")
            db.session.commit()

            self.mario_id = mario.id
            self.luigi_id = luigi.id

    def tearDown(self):
        """Clear any incomplete transactions."""
        with self.app.app_context():
            db.session.rollback()

    # Helper functions
    def login_user(self, http, user_id=None):
        """Helper function to log in a user."""
        # Change the session to mimic logging in,
        with http.session_transaction() as sess:
            sess[CURRENT_USER_KEY] = user_id or self.mario_id

    def is_get_route_as_anon_blocked(self, route):
        """Check that the route blocks anon users."""
        with self.app.test_client() as http:
            resp = http.get(route, follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", html)
            self.assert_routed_to_login(html)

    def is_post_route_as_anon_blocked(self, route, post_data={}):
        """Check that posting to the route blocks anon users."""
        with self.app.test_client() as http:
            resp = http.post(route, data=post_data, follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", html)
            self.assert_routed_to_login(html)

    def missing_item_returns_404(self, route):
        """Check that the route returns a 404 error for missing items."""
        with self.app.test_client() as http:
            self.login_user(http)
            resp = http.get(route)
            self.assertEqual(resp.status_code, 404)

    def assert_routed_to_landing(self, html):
        self.assertIn("Think you know baseball?", html)
        self.assertIn("<button>PLAY", html)

    def assert_routed_to_my_picks(self, html):
        self.assertIn("<h1>My Picks</h1>", html)

    def assert_routed_to_picksheet(self, html):
        self.assertIn("<h1>Make Your Picks</h1>", html)
        self.assertIn("Pick the teams you think will win!", html)
        self.assertIn("picks</button>", html)

    def assert_routed_to_scoreboard(self, html):
        self.assertIn("<h1>Scores & Schedule</h1>", html)
        self.assertIn("Your picks are marked with", html)
        self.assertIn("Scores update every 20 minutes.", html)

    def assert_routed_to_leaderboard(self, html):
        self.assertIn("<h1>Leaderboard</h1>", html)
        self.assertIn("<h5>Season</h5>", html)
        self.assertIn("mario", html)
        self.assertIn("luigi", html)

    def assert_routed_to_signup(self, html):
        self.assertIn("<h2>Sign up", html)
        self.assertIn("Username:", html)
        self.assertIn("Password:", html)
        self.assertIn("Confirm Password:", html)
        self.assertIn("(Optional) Image URL:", html)
        self.assertIn("<button>SIGN", html)

    def assert_routed_to_login(self, html):
        self.assertIn("<h2>Log in", html)
        self.assertIn("Username:", html)
        self.assertIn("Password:", html)
        self.assertIn("<button>LOG", html)

    def assert_routed_to_profile(self, html):
        self.assertIn("<h2>Edit Your Profile", html)
        self.assertIn("Username:", html)
        self.assertIn("(Optional) Image URL:", html)
        self.assertIn("To confirm your changes, enter your password:", html)
        self.assertIn("<button>UPDATE", html)

    def assert_routed_to_change_password(self, html):
        self.assertIn("<h2>Change Your Password", html)
        self.assertIn("Current Password:", html)
        self.assertIn("New Password:", html)
        self.assertIn("Confirm Password:", html)
        self.assertIn("<button>SAVE", html)
