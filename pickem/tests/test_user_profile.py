"""User Profile View tests."""
from .base import PickemTestCase

class UserProfileTestCase(PickemTestCase):
    """Tests for user profile routes."""
    def test_profile_form(self):
        """Does the edit profile form load?"""
        with self.app.test_client() as http:
            self.login_user(http)
            resp = http.get("/users/profile")
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("mario", html)
            self.assert_routed_to_profile(html)

    def test_profile_change(self):
        """Can the user edit his profile?"""
        with self.app.test_client() as http:
            self.login_user(http)
            post_data = {
                "username":"mario",
                "image_url":"https://nex.com/mario.jpeg",
                "password":"99coins"
            }
            resp = http.post("/users/profile", data=post_data, follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Your profile was updated.", html)
            self.assert_routed_to_my_picks(html)

    def test_profile_change_wrong_password(self):
        """Can the user edit his profile with the wrong password?"""
        with self.app.test_client() as http:
            self.login_user(http)
            post_data = {
                "username":"supermario",
                "image_url":"https://nes.com/mario.jpeg",
                "password":"peachispretty"
            }
            resp = http.post("/users/profile", data=post_data, follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Invalid credentials.", html)
            self.assert_routed_to_profile(html)

    def test_profile_change_username(self):
        """Can the user change his username?"""
        with self.app.test_client() as http:
            self.login_user(http)
            post_data = {"username":"supermario", "password":"99coins", "confirm":"99coins"}
            resp = http.post("/users/profile", data=post_data, follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Since you changed your username, we logged you off", html)
            self.assertIn("supermario", html) # Flash msg says "...log in with your new username: xxx"
            self.assert_routed_to_login(html)

            # Try logging in with the new username
            resp = http.post("/login", data=post_data, follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertIn("Hello, supermario!", html)
            self.assert_routed_to_my_picks(html)

    def test_profile_form_as_anon(self):
        """Is the profile page blocked when not logged in?"""
        self.is_get_route_as_anon_blocked("/users/profile")

    def test_profile_change_as_anon(self):
        """Is the profile submission blocked when not logged in?"""
        self.is_post_route_as_anon_blocked("/users/profile", {"image_url": "http://nes.com/bowser.jpeg"})
