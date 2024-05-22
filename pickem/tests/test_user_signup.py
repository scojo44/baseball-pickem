"""User Signup View tests."""
from .base import PickemTestCase

class UserSignupTestCase(PickemTestCase):
    """Tests for user signup routes."""
    def test_signup_form(self):
        """Does the sign up form load?"""
        with self.app.test_client() as http:
            resp = http.get("/signup")
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assert_routed_to_signup(html)

    def test_signup(self):
        """Can a new user sign up?"""
        with self.app.test_client() as http:
            post_data={"username": "peach", "password": "toadstool", "confirm": "toadstool"}
            resp = http.post("/signup", data=post_data, follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Welcome, peach,", html)
            self.assert_routed_to_my_picks(html)

    def test_signup_username_taken(self):
        """Does signup handle existing username gracefully?"""
        with self.app.test_client() as http:
            post_data={"username": "mario", "password": "goomba", "confirm": "goomba"}
            resp = http.post("/signup", data=post_data, follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Sorry, username mario is already taken.", html)
            self.assert_routed_to_signup(html)

    def test_signup_redirects_if_user_logged_in(self):
        """Does the signup page redirect for user already logged in?"""
        with self.app.test_client() as http:
            self.login_user(http)
            resp = http.get("/signup", follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assert_routed_to_my_picks(html)
