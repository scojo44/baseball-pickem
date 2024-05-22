"""User Admin View tests."""
from .base import PickemTestCase

# The Admin section is on the TODO list

class UserAdminTestCase(PickemTestCase):
    """Tests for user admin routes."""
    # User List Tests
    def test_list_users(self):
        """Does the user list work?"""
        with self.app.test_client() as http:
            self.login_user(http)
            resp = http.get("/users")
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("mario", html)
            self.assertIn("luigi", html)

    def test_list_users_by_anon(self):
        """Is the user list blocked for anon users?"""
        self.is_get_route_as_anon_blocked("/users")

    # Delete User Tests
    def test_delete_user(self):
        """Can the user delete his account?"""
        with self.app.test_client() as http:
            self.login_user(http)
            resp = http.post("/users/delete", follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Your account has been deleted.", html)
            self.assert_routed_to_landing(html)

    def test_delete_user_by_anon(self):
        """Can a user be deleted when not logged in?"""
        self.is_post_route_as_anon_blocked("/users/delete")
