"""Picksheet tests."""
import json
from app.models import User, Pick
from app.bp_game import UNSAVED_PICKS_KEY
from .base import PickemTestCase

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
            # Check for two objects with games for today and tomorrow
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

            # Update game IDs in the expected response
            fixed_april30_games = self.EXPECTED_RESPONSE_APRIL_30
            for game in [*fixed_april30_games['gamesToPick'][0]["games"], *fixed_april30_games['gamesToPick'][1]["games"]]:
                game["id"] += self.april30_first_game_id

            self.assertDictEqual(json, fixed_april30_games)

    def submit_picks(self, http):
        """Submit some sample picks against the mock API data."""
        # The JSON string from the <input> value is loaded to a dict on the server and saved to the session
        resp = http.post("/picksheet", data=self.SAMPLE_PICKS, follow_redirects=True)
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
                self.assertListEqual(picks, json.loads(self.SAMPLE_PICKS['picks']))

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
        for game_id in [15, 19, 20, 21, 22, 23, 24]:
            self.assertIn(str(self.april30_first_game_id + game_id), str(mario_picks))

    def test_submit_picks_for_picked_game(self):
        """Are picks for already picked games ignored?"""
        with self.app.test_client() as http:
            # Make some picks
            self.login_user(http)
            self.submit_picks(http)
            self.assert_picks_are_saved()

            # Try to pick the opposite team for a couple games
            picked_game1 = self.april30_first_game_id + 20
            picked_game2 = self.april30_first_game_id + 21
            repick_data = {
                'picks': json.dumps([
                    {"game": picked_game1, "team": 26}, # 8 was picked in sample picks
                    {"game": picked_game2, "team": 19}  # 1 was picked in sample picks
                ]
            )}

            resp = http.post("/picksheet", data=repick_data, follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assert_routed_to_my_picks(html)

            # Make sure those picks didn't change
            mario_picks = User.get(self.mario_id).picks
            test_picks = [p for p in mario_picks if p.game.id in (picked_game1, picked_game2)]
            self.assertEqual(test_picks[0].game.id, picked_game1)
            self.assertEqual(test_picks[1].game.id, picked_game2)
            self.assertEqual(test_picks[0].team.id, 8)
            self.assertEqual(test_picks[1].team.id, 1)

    def test_submit_picks_for_played_game(self):
        """Are picks for already played games ignored?"""
        with self.app.test_client() as http:
            # Try to pick a winning team and a losing team in these two games
            picked_game1 = self.april30_first_game_id
            picked_game2 = self.april30_first_game_id + 1
            repick_data = {
                'picks': json.dumps([
                    {"game": picked_game1, "team": 8}, # Wrong pick
                    {"game": picked_game2, "team": 11} # Correct pick
                ]
            )}

            self.login_user(http)
            resp = http.post("/picksheet", data=repick_data, follow_redirects=True)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assert_routed_to_my_picks(html)

            # Make sure those picks weren't saved
            mario_picks = User.get(self.mario_id).picks
            self.assertEqual(len(mario_picks), 1) # The sample pick in setUp()
            bad_picks = [p for p in mario_picks if p.game_id in [picked_game1, picked_game2]]
            self.assertEqual(len(bad_picks), 0)

    # Sample games to pick.
    # 'picks' is a hidden <input> whose value will be a JSON string.
    @property
    def SAMPLE_PICKS(self):
        return {
        'picks': json.dumps([
            {"game": self.april30_first_game_id + 15, "team": 28},
            {"game": self.april30_first_game_id + 19, "team": 6},
            {"game": self.april30_first_game_id + 20, "team": 8},
            {"game": self.april30_first_game_id + 21, "team": 1},
            {"game": self.april30_first_game_id + 22, "team": 13},
            {"game": self.april30_first_game_id + 23, "team": 9},
            {"game": self.april30_first_game_id + 24, "team": 7}
        ])
    }

    @property
    def EXPECTED_RESPONSE_APRIL_30(self):
        return {
        "gamesToPick": [
            {
                "date": "Wednesday, April 30",
                "games": [
                    {
                        "apiID": 401695362,
                        "awayTeam": {
                            "abbreviation": "ATH",
                            "apiID": 11,
                            "errors": "-",
                            "hits": "-",
                            "id": 2,
                            "leagueID": 1,
                            "location": "",
                            "logoURL": "https://a.espncdn.com/i/teamlogos/mlb/500/ath.png",
                            "name": "Athletics",
                            "score": "-",
                        },
                        "homeTeam": {
                            "abbreviation": "TEX",
                            "apiID": 13,
                            "errors": "-",
                            "hits": "-",
                            "id": 28,
                            "leagueID": 1,
                            "location": "Texas",
                            "logoURL": "https://a.espncdn.com/i/teamlogos/mlb/500/tex.png",
                            "name": "Rangers",
                            "score": "-",
                        },
                        "id": 15,
                        "startTime": "2025-04-30T17:05:00-07:00",
                        "status": "Scheduled",
                        "statusDetail": "4/30 - 8:05 PM EDT",
                        "subseasonID": 1,
                        "winTeamID": None,
                    }
                ],
            },
            {
                "date": "Thursday, May 1",
                "games": [
                    {
                        "apiID": 401695369,
                        "awayTeam": {
                            "abbreviation": "CHC",
                            "apiID": 16,
                            "errors": 1,
                            "hits": 11,
                            "id": 6,
                            "leagueID": 1,
                            "location": "Chicago",
                            "logoURL": "https://a.espncdn.com/i/teamlogos/mlb/500/chc.png",
                            "name": "Cubs",
                            "score": 8,
                        },
                        "homeTeam": {
                            "abbreviation": "PIT",
                            "apiID": 23,
                            "errors": "-",
                            "hits": 5,
                            "id": 22,
                            "leagueID": 1,
                            "location": "Pittsburgh",
                            "logoURL": "https://a.espncdn.com/i/teamlogos/mlb/500/pit.png",
                            "name": "Pirates",
                            "score": 3,
                        },
                        "id": 19,
                        "startTime": "2025-05-01T09:35:00-07:00",
                        "status": "Scheduled",
                        "statusDetail": "4/30 - 8:05 PM EDT",
                        "subseasonID": 1,
                        "winTeamID": None,
                    },
                    {
                        "apiID": 401695372,
                        "awayTeam": {
                            "abbreviation": "STL",
                            "apiID": 24,
                            "errors": 1,
                            "hits": 3,
                            "id": 26,
                            "leagueID": 1,
                            "location": "St. Louis",
                            "logoURL": "https://a.espncdn.com/i/teamlogos/mlb/500/stl.png",
                            "name": "Cardinals",
                            "score": 1,
                        },
                        "homeTeam": {
                            "abbreviation": "CIN",
                            "apiID": 17,
                            "errors": 1,
                            "hits": 9,
                            "id": 8,
                            "leagueID": 1,
                            "location": "Cincinnati",
                            "logoURL": "https://a.espncdn.com/i/teamlogos/mlb/500/cin.png",
                            "name": "Reds",
                            "score": 9,
                        },
                        "id": 20,
                        "startTime": "2025-05-01T09:40:00-07:00",
                        "status": "Scheduled",
                        "statusDetail": "4/30 - 8:05 PM EDT",
                        "subseasonID": 1,
                        "winTeamID": None,
                    },
                    {
                        "apiID": 401695367,
                        "awayTeam": {
                            "abbreviation": "ARI",
                            "apiID": 29,
                            "errors": "-",
                            "hits": 9,
                            "id": 1,
                            "leagueID": 1,
                            "location": "Arizona",
                            "logoURL": "https://a.espncdn.com/i/teamlogos/mlb/500/ari.png",
                            "name": "Diamondbacks",
                            "score": 4,
                        },
                        "homeTeam": {
                            "abbreviation": "NYM",
                            "apiID": 21,
                            "errors": 2,
                            "hits": 5,
                            "id": 19,
                            "leagueID": 1,
                            "location": "New York",
                            "logoURL": "https://a.espncdn.com/i/teamlogos/mlb/500/nym.png",
                            "name": "Mets",
                            "score": 2,
                        },
                        "id": 21,
                        "startTime": "2025-05-01T10:10:00-07:00",
                        "status": "Scheduled",
                        "statusDetail": "4/30 - 8:05 PM EDT",
                        "subseasonID": 1,
                        "winTeamID": None,
                    },
                    {
                        "apiID": 401695370,
                        "awayTeam": {
                            "abbreviation": "KC",
                            "apiID": 7,
                            "errors": "-",
                            "hits": 15,
                            "id": 13,
                            "leagueID": 1,
                            "location": "Kansas City",
                            "logoURL": "https://a.espncdn.com/i/teamlogos/mlb/500/kc.png",
                            "name": "Royals",
                            "score": 8,
                        },
                        "homeTeam": {
                            "abbreviation": "TB",
                            "apiID": 30,
                            "errors": "-",
                            "hits": 8,
                            "id": 27,
                            "leagueID": 1,
                            "location": "Tampa Bay",
                            "logoURL": "https://a.espncdn.com/i/teamlogos/mlb/500/tb.png",
                            "name": "Rays",
                            "score": 2,
                        },
                        "id": 22,
                        "startTime": "2025-05-01T10:10:00-07:00",
                        "status": "Scheduled",
                        "statusDetail": "4/30 - 8:05 PM EDT",
                        "subseasonID": 1,
                        "winTeamID": None,
                    },
                    {
                        "apiID": 401695371,
                        "awayTeam": {
                            "abbreviation": "MIN",
                            "apiID": 9,
                            "errors": "-",
                            "hits": 13,
                            "id": 18,
                            "leagueID": 1,
                            "location": "Minnesota",
                            "logoURL": "https://a.espncdn.com/i/teamlogos/mlb/500/min.png",
                            "name": "Twins",
                            "score": 3,
                        },
                        "homeTeam": {
                            "abbreviation": "CLE",
                            "apiID": 5,
                            "errors": "-",
                            "hits": 6,
                            "id": 9,
                            "leagueID": 1,
                            "location": "Cleveland",
                            "logoURL": "https://a.espncdn.com/i/teamlogos/mlb/500/cle.png",
                            "name": "Guardians",
                            "score": 4,
                        },
                        "id": 23,
                        "startTime": "2025-05-01T10:10:00-07:00",
                        "status": "Scheduled",
                        "statusDetail": "4/30 - 8:05 PM EDT",
                        "subseasonID": 1,
                        "winTeamID": None,
                    },
                    {
                        "apiID": 401695374,
                        "awayTeam": {
                            "abbreviation": "MIL",
                            "apiID": 8,
                            "errors": 1,
                            "hits": 2,
                            "id": 17,
                            "leagueID": 1,
                            "location": "Milwaukee",
                            "logoURL": "https://a.espncdn.com/i/teamlogos/mlb/500/mil.png",
                            "name": "Brewers",
                            "score": "-",
                        },
                        "homeTeam": {
                            "abbreviation": "CHW",
                            "apiID": 4,
                            "errors": 1,
                            "hits": 9,
                            "id": 7,
                            "leagueID": 1,
                            "location": "Chicago",
                            "logoURL": "https://a.espncdn.com/i/teamlogos/mlb/500/chw.png",
                            "name": "White Sox",
                            "score": 8,
                        },
                        "id": 24,
                        "startTime": "2025-05-01T11:10:00-07:00",
                        "status": "Scheduled",
                        "statusDetail": "4/30 - 8:05 PM EDT",
                        "subseasonID": 1,
                        "winTeamID": None,
                    },
                ],
            },
        ]
    }
