"""User Login & Logout View tests."""
from .base import PickemTestCase

class UserLoginLogoutTestCase(PickemTestCase):
    """Tests for user login/logout routes."""
    # Login Tests
    def test_login_form(self):
        """Does the login form load?"""
        with self.app.test_client() as http:
            resp = http.get("/login")
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assert_routed_to_login(html)

    def test_login(self):
        """Can a user log in?"""
        with self.app.test_client() as http:
            post_data={"username": "mario", "password": "99coins"}
            resp = http.post("/login", data=post_data, follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Hello, mario!", html)
            self.assert_routed_to_my_picks(html)

    def test_login_wrong_password(self):
        """Can a user log in with the wrong password?"""
        with self.app.test_client() as http:
            post_data={"username": "mario", "password": "fireball99"}
            resp = http.post("/login", data=post_data, follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Invalid credentials.", html)
            self.assert_routed_to_login(html)

    def test_login_redirects_if_user_logged_in(self):
        """Does the login page redirect for user already logged in?"""
        with self.app.test_client() as http:
            self.login_user(http)
            resp = http.get("/login", follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assert_routed_to_my_picks(html)

    # Logout Tests
    def test_logout(self):
        """Can the user log out?"""
        with self.app.test_client() as http:
            self.login_user(http)
            resp = http.get("/logout", follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("You have been logged out.", html)
            self.assert_routed_to_landing(html)

    def test_logout_as_anon(self):
        """Doe the logout route just redirect to the landing page if not logged in?"""
        with self.app.test_client() as http:
            resp = http.get("/logout", follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assert_routed_to_landing(html)
