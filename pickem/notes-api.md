
baseball.api-sports.io
======================

MLB Leagues and Divisions
-------------------------

https://v1.baseball.api-sports.io/standings

    0: "American League"
    1: "National League"
    2: "AL East"
    3: "AL Central"
    4: "AL West"
    5: "NL East"
    6: "NL Central"
    7: "NL West"

ESPN Test
---------

    from datetime import datetime
    from .models import Sport, League, Team, Season, SubSeason, SubSeasonType
    ESPN_API = 'http://site.api.espn.com/apis/site/v2/sports/'
    log = ''

    r = requests.get(ESPN_API + 'baseball/mlb/teams')

    # Get the sport info
    r_sport = r.json()['sports'][0]
    sport = Sport.create_from_espn(r_sport)
    sport.save()

    # Get the league info
    r_league = r_sport['leagues'][0]
    league = League.create_from_espn(r_league, sport.id)
    league.save()

    # Hard-code the seasons for now
    season = Season('2024', 2024, league.id)
    season.save()
    subseason = SubSeason('Regular Season', SubSeasonType.regular, datetime(2024, 3, 28), datetime(2024, 10, 1), season.id)
    subseason.save()

    # Get the teams
    r_teams = r_league['teams']
    for r_team in r_teams:
        team = r_team['team']
        Team.create_from_espn(team, league.id)

    r = requests.get(ESPN_API + 'baseball/mlb/scoreboard')
    # games = r.json()['events']

    return str(sport)
