"""Picksheet tests."""
import json
from app.models import User, Pick
from app.bp_game import UNSAVED_PICKS_KEY
from .base import PickemTestCase

# Sample games to pick from Sept 8, 2024.  Will have to update this later
# 'picks' is a hidden <input> whose value will be a JSON string
SAMPLE_PICKS = {'picks': '''[
    {"game":"2613","team":"3"},
    {"game":"2614","team":"2"},
    {"game":"2615","team":"4"},
    {"game":"2616","team":"22"},
    {"game":"2617","team":"15"},
    {"game":"2618","team":"18"},
    {"game":"2619","team":"11"},
    {"game":"2620","team":"12"}
]'''}

class PicksheetTestCase(PickemTestCase):
    """Tests for Picksheet routes."""
    def test_picksheet(self):
        """Does the picksheet form load?"""
        with self.app.test_client() as http:
            resp = http.get("/picksheet")
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assert_routed_to_picksheet(html)

    def test_picksheet_games_api(self):
        """Are a collection of pickable games returned?"""
        with self.app.test_client() as http:
            self.login_user(http)
            resp = http.get("/picksheet/games")
            json = resp.get_json()
            self.assertEqual(resp.status_code, 200)
            # Since the available games can vary, check for two objects for today and tomorrow.
            self.assertIsNotNone(json['gamesToPick'])
            self.assertEqual(len(json['gamesToPick']), 2)
            # Each will have a date as a string and an array of games
            self.assertIsNotNone(json['gamesToPick'][0]['date'])
            self.assertIsNotNone(json['gamesToPick'][0]['games'])
            self.assertIsInstance(json['gamesToPick'][0]['date'], str)
            self.assertIsInstance(json['gamesToPick'][0]['games'], list)
            self.assertIsNotNone(json['gamesToPick'][1]['date'])
            self.assertIsNotNone(json['gamesToPick'][1]['games'])
            self.assertIsInstance(json['gamesToPick'][1]['date'], str)
            self.assertIsInstance(json['gamesToPick'][1]['games'], list)

    def submit_picks(self, http):
        """Submit some sample picks against the mock API data."""
        # The JSON string from the <input> value is loaded to a dict on the server and saved to the session
        resp = http.post("/picksheet", data=SAMPLE_PICKS, follow_redirects=True)
        html = resp.get_data(as_text=True)
        self.assertEqual(resp.status_code, 200)
        return html

    def test_submit_picks(self):
        """Are the picks accepted and saved to the database for a logged in user?"""
        with self.app.test_client() as http:
            self.login_user(http)
            html = self.submit_picks(http)
            self.assert_routed_to_my_picks(html)
            self.assert_picks_are_saved()

    def test_submit_picks_as_anon(self):
        """Are the picks accepted, temporarily stored in the session, then saved to the database after the user logs in?"""
        with self.app.test_client() as http:
            html = self.submit_picks(http)
            # Submitting picks as guest goes to the signup page where the guest can sign up or go to the login page
            self.assert_routed_to_signup(html)

            # Now the session should have the list of picks (the JSON string in the above input value)
            with http.session_transaction() as sess:
                picks = sess.get(UNSAVED_PICKS_KEY)
                # The server has to get the JSON string from the <input> value, then parse the JSON into a list
                self.assertListEqual(picks, json.loads(SAMPLE_PICKS['picks']))

            # Log in the user and go to the My Picks page
            self.login_user(http)
            resp = http.get("/mypicks")
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assert_routed_to_my_picks(html)
            self.assert_picks_are_saved()

    def assert_picks_are_saved(self):
        """Are the picks saved to the database?"""
        mario_picks = User.get(self.mario_id).picks
        self.assertIn('2613', str(mario_picks))
        self.assertIn('2614', str(mario_picks))
        self.assertIn('2615', str(mario_picks))
        self.assertIn('2616', str(mario_picks))
        self.assertIn('2617', str(mario_picks))
        self.assertIn('2618', str(mario_picks))
        self.assertIn('2619', str(mario_picks))
        self.assertIn('2620', str(mario_picks))

    def test_submit_picks_for_picked_game(self):
        """Are picks for already picked games ignored?"""
        with self.app.test_client() as http:
            # Make some picks
            self.login_user(http)
            self.submit_picks(http)
            self.assert_picks_are_saved()

            # Try to pick the opposite team for a couple games
            repick_data = {'picks': '[{"game":"2615","team":"6"},{"game":"2620","team":"17"}]'}
            resp = http.post("/picksheet", data=repick_data, follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assert_routed_to_my_picks(html)

            # Make sure those picks didn't change
            mario_picks = User.get(self.mario_id).picks
            test_picks = [p for p in mario_picks if p.game.id in (2615, 2620)]
            self.assertEqual(test_picks[0].game.id, 2615)
            self.assertEqual(test_picks[1].game.id, 2620)
            self.assertEqual(test_picks[0].team.id, 4)
            self.assertEqual(test_picks[1].team.id, 12)

    def test_submit_picks_for_played_game(self):
        """Are picks for already played games ignored?"""
        with self.app.test_client() as http:
            # Try to pick the opposite team for a couple games
            self.login_user(http)
            repick_data = {'picks': '[{"game":"500","team":"2"},{"game":"700","team":"18"}]'}
            resp = http.post("/picksheet", data=repick_data, follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assert_routed_to_my_picks(html)

            # Make sure those picks weren't saved
            mario_picks = User.get(self.mario_id).picks
            self.assertEqual(len(mario_picks), 0)
