"""My Picks tests."""
from .base import PickemTestCase

class MyPicksTestCase(PickemTestCase):
    """Tests for My Picks routes."""
    def test_my_picks(self):
        """Does the My Picks page load?"""
        with self.app.test_client() as http:
            self.login_user(http)
            resp = http.get("/mypicks")
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assert_routed_to_my_picks(html)

    def test_my_picks_as_anon(self):
        """Is the My Picks page blocked when not logged in?"""
        self.is_get_route_as_anon_blocked("/mypicks")
