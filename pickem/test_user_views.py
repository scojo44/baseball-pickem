"""User View tests."""
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

class MessageViewTestCase(TestCase):
    """Test views for messages."""

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

    # Signup Tests
    def test_signup_form(self):
        """Does the sign up form load?"""
        with app.test_client() as http:
            resp = http.get("/signup")
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Username", html)
            self.assertIn("Password", html)
            self.assertIn("Confirm", html)

    def test_signup(self):
        """Can a new user sign up?"""
        with app.test_client() as http:
            post_data={"username": "peach", "password": "toadstool"}
            resp = http.post("/signup", data=post_data, follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("@peach", html)

    def test_signup_username_taken(self):
        """Does signup handle existing username gracefully?"""
        with app.test_client() as http:
            post_data={"username": "mario", "password": "goomba"}
            resp = http.post("/signup", data=post_data, follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Sorry, username @mario is already taken.", html)

    def test_signup_redirects_if_user_logged_in(self):
        """Does the signup page redirect for user already logged in?"""
        with app.test_client() as http:
            self.login_user(http)
            resp = http.get("/signup", follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("@mario", html)

    # Login Tests
    def test_login_form(self):
        """Does the login form load?"""
        with app.test_client() as http:
            resp = http.get("/login")
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Username", html)
            self.assertIn("Password", html)

    def test_login(self):
        """Can a user log in?"""
        with app.test_client() as http:
            post_data={"username": "mario", "password": "99coins"}
            resp = http.post("/login", data=post_data, follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Hello, mario!", html)
            self.assertIn("@mario", html)

    def test_login_wrong_password(self):
        """Can a user log in with the wrong password?"""
        with app.test_client() as http:
            post_data={"username": "mario", "password": "fireball99"}
            resp = http.post("/login", data=post_data, follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Invalid credentials.", html)

    def test_login_redirects_if_user_logged_in(self):
        """Does the login page redirect for user already logged in?"""
        with app.test_client() as http:
            self.login_user(http)
            resp = http.get("/login", follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("@mario", html)

    # Logout Tests
    def test_logout(self):
        """Can the user log out?"""
        with app.test_client() as http:
            self.login_user(http)
            resp = http.get("/logout", follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("You have been logged out.", html)

    # User List Tests
    def test_list_users(self):
        """Does the user list work?"""
        with app.test_client() as http:
            self.login_user(http)
            resp = http.get("/users")
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("@mario", html)
            self.assertIn("@luigi", html)

    def test_list_users_with_search(self):
        """Does the user list work?"""
        with app.test_client() as http:
            self.login_user(http)
            resp = http.get("/users?q=luigi")
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("@luigi", html)

    # User Display Tests
    def test_users_messages(self):
        """Can the user view another user's profile?"""
        with app.test_client() as http:
            self.login_user(http)
            resp = http.get(f"/users/{self.luigi_id}")
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("@luigi", html)

    # Edit Profile Tests
    def test_profile_form(self):
        """Does the edit profile form load?"""
        with app.test_client() as http:
            self.login_user(http)
            resp = http.get("/users/profile")
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Username", html)
            self.assertIn("To confirm changes, enter your password:", html)
            self.assertIn("mario", html)

    def test_profile_change(self):
        """Can the user edit his profile?"""
        with app.test_client() as http:
            self.login_user(http)
            post_data = {"email":"a.me@supermario.com", "password":"99coins"}
            resp = http.post("/users/profile", data=post_data, follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Your profile was updated.", html)
            self.assertIn("@mario", html)

    def test_profile_change(self):
        """Can the user edit his profile with the wrong password?"""
        with app.test_client() as http:
            self.login_user(http)
            post_data = {"email":"a.me@supermario.com", "password":"peachispretty"}
            resp = http.post("/users/profile", data=post_data, follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Invalid credentials.", html)

    def test_profile_change_username(self):
        """Can the user change his username?"""
        with app.test_client() as http:
            self.login_user(http)
            post_data = {"username":"supermario", "password":"99coins"}
            resp = http.post("/users/profile", data=post_data, follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Since you changed your username, we logged you off", html)
            self.assertIn("Username", html) # Redirected to the login page
            self.assertIn("Password", html)
            # Try logging in with the new username
            resp = http.post("/login", data=post_data, follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertIn("Hello, supermario!", html)
            self.assertIn("@supermario", html)

    def test_profile_form_as_anon(self):
        """Is the profile page blocked when not logged in?"""
        self.is_get_route_as_anon_blocked("/users/profile")

    def test_profile_change_as_anon(self):
        """Is the profile page blocked when not logged in?"""
        self.is_post_route_as_anon_blocked("/users/profile", {"email": "test@foo.com"})
    
    # Delete User Tests
    def test_delete_user(self):
        """Can the user delete his account?"""
        with app.test_client() as http:
            self.login_user(http)
            resp = http.post("/users/delete", follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Your account and any warbles have been deleted.", html)

    def test_delete_user_by_anon(self):
        """Can a user be deleted when not logged in?"""
        self.is_post_route_as_anon_blocked("/users/delete")
