"""Leaderboard tests."""
from .base import PickemTestCase

LEADERS_APRIL_1 = {
    "day": "2024-04-01",
    "dayDisplay": "Mon, April 1",
    "nextDay": "2024-04-02",
    "prevDay": "2024-03-31",
    "users": [
        {
        "name": "mario",
        "points": 0
        },
        {
        "name": "luigi",
        "points": 0
        }
    ]
}

class LeaderboardTestCase(PickemTestCase):
    """Tests for Leaderboard routes."""
    def test_leaderboard(self):
        """Does the Leaderboard load?"""
        with self.app.test_client() as http:
            self.login_user(http)
            resp = http.get("/leaderboard")
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assert_routed_to_leaderboard(html)

    def test_leaderboard_as_anon(self):
        """Is the Leaderboard blocked when not logged in?"""
        self.is_get_route_as_anon_blocked("/leaderboard")

    def test_leaderboard_users_api(self):
        """Is a list of the top users returned as JSON?"""
        with self.app.test_client() as http:
            self.login_user(http)
            resp = http.get("/leaderboard/users/2024-04-01")
            json = resp.get_json()
            self.assertEqual(resp.status_code, 200)
            self.assertDictEqual(json, LEADERS_APRIL_1)
