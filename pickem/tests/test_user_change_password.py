"""User Change Password View tests."""
from .base import PickemTestCase

class UserChangePasswordTestCase(PickemTestCase):
    """Tests for user change password routes."""
    def test_change_password_form(self):
        """Does the change password form load?"""
        with self.app.test_client() as http:
            self.login_user(http)
            resp = http.get("/users/password")
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assert_routed_to_change_password(html)

    def test_change_password(self):
        """Can the user change his password?"""
        with self.app.test_client() as http:
            self.login_user(http)
            post_data = {
                "password":"99coins",
                "new_password":"99rupees",
                "confirm":"99rupees"
            }
            resp = http.post("/users/password", data=post_data, follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Your password was changed.", html)
            self.assert_routed_to_my_picks(html)

    def test_change_password_wrong_password(self):
        """Can the user change his password with the wrong current password?"""
        with self.app.test_client() as http:
            self.login_user(http)
            post_data = {
                "password":"9999coins",
                "new_password":"99rupees",
                "confirm":"99rupees"
            }
            resp = http.post("/users/password", data=post_data, follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Invalid credentials.", html)
            self.assert_routed_to_change_password(html)

    def test_change_password_form_as_anon(self):
        """Is the change password page blocked when not logged in?"""
        self.is_get_route_as_anon_blocked("/users/password")

    def test_change_password_as_anon(self):
        """Is the change password submission blocked when not logged in?"""
        self.is_post_route_as_anon_blocked("/users/password", {
            "password":"99coins",
            "new_password":"99rupees",
            "confirm":"99rupees"
        })
