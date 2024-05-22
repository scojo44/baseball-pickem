"""Scoreboard tests."""
from .base import PickemTestCase

class ScoreboardTestCase(PickemTestCase):
    """Tests for Scoreboard routes."""
    def test_scoreboard(self):
        """Does the Scoreboard load?"""
        with self.app.test_client() as http:
            self.login_user(http)
            resp = http.get("/scoreboard")
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assert_routed_to_scoreboard(html)

    def test_scoreboard_as_anon(self):
        """Is the Scoreboard blocked when not logged in?"""
        self.is_get_route_as_anon_blocked("/scoreboard")

    def test_scoreboard_games_api(self):
        """Are a collection of games with scores returned as JSON?"""
        with self.app.test_client() as http:
            self.login_user(http)
            resp = http.get("/scoreboard/games/2024-04-18")
            json = resp.get_json()
            self.assertEqual(resp.status_code, 200)
            self.assertDictEqual(json, self.SCORES_APRIL_18)

    def test_scoreboard_games_api_not_a_game_day(self):
        """Is JSON returned for a day with no games?"""
        with self.app.test_client() as http:
            self.login_user(http)
            resp = http.get("/scoreboard/games/2024-01-01")
            json = resp.get_json()
            self.assertEqual(resp.status_code, 200)
            self.assertDictEqual(json, self.SCORES_JAN_1)

    SCORES_JAN_1 = {
        "day": "2024-01-01",
        "dayDisplay": "Mon, January 1",
        "games": [],
        "nextDay": "2024-01-02",
        "prevDay": "2023-12-31",
        "userPoints": 0
    }

    SCORES_APRIL_18 = {
        "day": "2024-04-18",
        "dayDisplay": "Thu, April 18",
        "games": [
            {
            "apiID": 153509,
            "awayTeam": {
                "abbreviation": "TEX",
                "apiID": 35,
                "errors": 0,
                "hits": 13,
                "id": 28,
                "leagueID": 1,
                "location": "Texas",
                "logoURL": "https://a.espncdn.com/i/teamlogos/mlb/500/tex.png",
                "name": "Rangers",
                "score": 9
            },
            "homeTeam": {
                "abbreviation": "DET",
                "apiID": 12,
                "errors": 3,
                "hits": 11,
                "id": 10,
                "leagueID": 1,
                "location": "Detroit",
                "logoURL": "https://a.espncdn.com/i/teamlogos/mlb/500/det.png",
                "name": "Tigers",
                "score": 7
            },
            "id": 754,
            "pick": None,
            "startTime": "2024-04-18T10:10:00-07:00",
            "status": "Final",
            "subseasonID": 1,
            "winTeamID": 28
            },
            {
            "apiID": 153510,
            "awayTeam": {
                "abbreviation": "LAA",
                "apiID": 17,
                "errors": 0,
                "hits": 6,
                "id": 13,
                "leagueID": 1,
                "location": "Los Angeles",
                "logoURL": "https://a.espncdn.com/i/teamlogos/mlb/500/laa.png",
                "name": "Angels",
                "score": 1
            },
            "homeTeam": {
                "abbreviation": "TB",
                "apiID": 34,
                "errors": 1,
                "hits": 5,
                "id": 27,
                "leagueID": 1,
                "location": "Tampa Bay",
                "logoURL": "https://a.espncdn.com/i/teamlogos/mlb/500/tb.png",
                "name": "Rays",
                "score": 2
            },
            "id": 755,
            "pick": None,
            "startTime": "2024-04-18T10:10:00-07:00",
            "status": "Final",
            "subseasonID": 1,
            "winTeamID": 27
            },
            {
            "apiID": 153511,
            "awayTeam": {
                "abbreviation": "CLE",
                "apiID": 9,
                "errors": 2,
                "hits": 8,
                "id": 8,
                "leagueID": 1,
                "location": "Cleveland",
                "logoURL": "https://a.espncdn.com/i/teamlogos/mlb/500/cle.png",
                "name": "Guardians",
                "score": 5
            },
            "homeTeam": {
                "abbreviation": "BOS",
                "apiID": 5,
                "errors": 2,
                "hits": 6,
                "id": 4,
                "leagueID": 1,
                "location": "Boston",
                "logoURL": "https://a.espncdn.com/i/teamlogos/mlb/500/bos.png",
                "name": "Red Sox",
                "score": 4
            },
            "id": 756,
            "pick": None,
            "startTime": "2024-04-18T10:35:00-07:00",
            "status": "Final",
            "subseasonID": 1,
            "winTeamID": 8
            },
            {
            "apiID": 153513,
            "awayTeam": {
                "abbreviation": "ARI",
                "apiID": 2,
                "errors": 1,
                "hits": 3,
                "id": 1,
                "leagueID": 1,
                "location": "Arizona",
                "logoURL": "https://a.espncdn.com/i/teamlogos/mlb/500/ari.png",
                "name": "Diamondbacks",
                "score": 0
            },
            "homeTeam": {
                "abbreviation": "SF",
                "apiID": 31,
                "errors": 0,
                "hits": 8,
                "id": 24,
                "leagueID": 1,
                "location": "San Francisco",
                "logoURL": "https://a.espncdn.com/i/teamlogos/mlb/500/sf.png",
                "name": "Giants",
                "score": 5
            },
            "id": 757,
            "pick": None,
            "startTime": "2024-04-18T18:45:00-07:00",
            "status": "Final",
            "subseasonID": 1,
            "winTeamID": 24
            }
        ],
        "nextDay": "2024-04-19",
        "prevDay": "2024-04-17",
        "userPoints": 0
    }
