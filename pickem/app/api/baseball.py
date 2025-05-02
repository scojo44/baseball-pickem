"""Baseball API updates provided by api-sports.io"""
import os
import json
import requests
from datetime import datetime, date, timedelta
from time import sleep
from flask import current_app as app
from ..extensions import scheduler
from ..models import db, Sport, League, Team, Season, SubSeason, SubSeasonType, Game

API_ESPN_PREFIX = 'http://site.api.espn.com/apis/site/v2/sports/baseball/mlb/'

def call_espn_api(endpoint: str, params: dict = None) -> dict:
    """Call the ESPN API."""
    try:
        resp = requests.get(API_ESPN_PREFIX + endpoint, params)
        return resp.json()

    except(requests.ConnectionError, requests.Timeout, requests.TooManyRedirects, requests.JSONDecodeError):
        return None  # Ignore the error and signal by returning None

def get_api_games(date: date = None) -> list:
    """Get games from the API.  Past and ongoing games will have scores.
    
    params is a dict of query parameters:
    - dates: date string in like yyyymmdd or a range like yyyymmdd-yyyymmdd
      Omitting this will return today's games
    """

    if date:
        params = {}
        params['dates'] = date.strftime('%Y%m%d')

    resp = call_espn_api('scoreboard', params)
    if not resp:
        return []

    return resp['leagues'][0], resp['events'] # League info, the list of games

def handle_api_errors(error):
    """Handle errors returned from the API."""
    print('=== pickem ===', 'API Error:', error)

def parse_int(value: str, default_value: int):
    """Parse integer from string without crashing."""
    try:
        return int(value)
    except(ValueError):
        return default_value

def add_game(api_game: dict, league: League, subseason: SubSeason) -> None:
    """Save a game to the database."""
    add_or_update_game(api_game, None, league, subseason)

def update_game(api_game: dict, db_game: Game, league: League) -> None:
    """Update a game in the database."""
    add_or_update_game(api_game, db_game, league)

def add_or_update_game(api_game: dict, game: Game, league: League, subseason: SubSeason = None) -> None:
    """Add a new or update an existing game in the database."""
    # Check for missing teams.  All-star teams are not included in ESPN's /teams endpoint.
    for team in [team['team'] for team in api_game['competitors']]:
        # Convert some integer values from strings in ESPN's API response
        team_api_id = parse_int(team['id'], 0)
        if team_api_id == 0:
            continue

        if not Team.get_first(db.select(Team).where(Team.league_id == league.id).where(Team.api_id == team_api_id)):
            add_team(team, league.id)

    for team in api_game['competitors']:
        if team['homeAway'] == 'away':  away_team = team
        if team['homeAway'] == 'home':  home_team = team

    select_ateam = db.select(Team).where(Team.api_id == away_team['id'])
    select_hteam = db.select(Team).where(Team.api_id == home_team['id'])

    # Convert some integer values from strings in ESPN's API response
    game_status = parse_int(api_game['status']['type']['id'], 3)
    away_score = parse_int(away_team['score'], 0)
    home_score = parse_int(home_team['score'], 0)

    if game: # Existing game:  Update scores and other info
        game.status = game_status
        game.status_detail = api_game['status']['type']['shortDetail']
        game.away_score = away_score
        game.home_score = home_score
        game.away_hits = away_team['hits']
        game.home_hits = home_team['hits']
        game.away_errors = away_team['errors']
        game.home_errors = home_team['errors']
        # Start time could change for doubleheaders and TV network demands
        game.start = datetime.fromisoformat(api_game['date'])
        # These shouldn't change but update them just in case
        game.away_team_id = Team.get_first(select_ateam).id
        game.home_team_id = Team.get_first(select_hteam).id
    else: # New game
        game = Game(
            start = datetime.fromisoformat(api_game['date']),
            away_team_id = Team.get_first(select_ateam).id,
            home_team_id = Team.get_first(select_hteam).id,
            api_id = api_game['id'],
            subseason_id = subseason.id,
            status = game_status,
            status_detail = api_game['status']['type']['shortDetail'],
            away_score = away_score,
            home_score = home_score,
            away_hits = away_team['hits'],
            home_hits = home_team['hits'],
            away_errors = away_team['errors'],
            home_errors = home_team['errors']
        )

    if not game.save():
        print("=== pickem ===", game.away_team, game.get_last_error())

def add_team(team: dict, league_id: int) -> None:
    """Save a team to the database."""
    # ESPN uses Athletics for both.  The Athletics do not currently associate with a location.
    location = team['location'] if team['location'] != team['name'] else ''
    logo_url = team['logos'][0]['href'] if team.get('logos') else team['logo']

    new_team = Team(
        team['name'],
        location,
        team['abbreviation'],
        logo_url,
        team['id'],
        league_id
    )

    if not new_team.save():
        print("=== pickem ===", team, team.get_last_error())

def update_team(db_team: Team, api_team: dict) -> None:
    """Update a team to the database."""
    # ESPN uses Athletics for both.  The Athletics do not currently associate with a location.
    location = api_team['location'] if api_team['location'] != api_team['name'] else ''
    logo_url = api_team['logos'][0]['href'] if api_team.get('logos') else api_team['logo']
    db_team.name = api_team['name']
    db_team.location = location
    db_team.abbreviation = api_team['abbreviation']
    db_team.logo_url = logo_url

    if not db_team.save():
        print("=== pickem ===", db_team, db_team.get_last_error())

# These three functions are called by the scheduler.  Jobs are defined in the config file.
def check_for_metadata_updates(): # Runs once per day
    """Check for changes to teams and game schedules."""
    with scheduler.app.app_context():
        # Check for teams that moved and/or changed their names.
        check_for_league_updates()
        # Check for schedule updates for the next day's games.
        check_for_updates(datetime.now().date() + timedelta(days=1))

def check_for_late_game_scores(): # Runs once per day
    """Check scores for yesterday's late games."""
    with scheduler.app.app_context():
        check_for_updates(datetime.now().date() - timedelta(days=1))

def check_for_score_updates(): # Runs every twenty minutes
    """Check for the latest game scores."""
    with scheduler.app.app_context():
        check_for_updates()

def check_for_updates(day: date = date.today()) -> None:
    """Update game records with current scores, changed start times.
    Add games that were not on the original schedule.
    Delete games that no longer exist."""
    print("=== pickem === ", day, "Updating game scores from API...")

    # Get the day's games from the API
    try:
        api_league, api_games = get_api_games(day) if not app.testing else get_test_data('espn_scoreboard.json')
    except Exception as e:
        handle_api_errors(e)
        return

    # Get the day's games from the database
    select_by_day = db.select(Game).where(Game.start_time.between(day, day + timedelta(days=1)))
    saved_games: list[Game] = Game.get_all(select_by_day)

    # Remove games in the database that no longer exist
    for db_game in saved_games:
        game_scheduled = False

        for game in api_games:
            if game['id'] == db_game.api_id:
                game_scheduled = True

        if not game_scheduled:
            db_game.delete()

    # Get the current league and season
    league_api_id = parse_int(api_league['id'], 0)
    if league_api_id > 0:
        league = League.get_first(db.select(League).where(League.api_id == league_api_id))
        if league is not None:
            season = Season.get_first(db.select(Season).where(Season.league_id == league.id and Season.year == api_league['season']['year']))
            subseason = SubSeason.get_first(db.select(SubSeason).where(SubSeason.season_id == season.id))

    # Check for new games and updates to existing games
    for api_game in [game['competitions'][0] for game in api_games]:
        # Convert some integer values from strings in ESPN's API response
        game_api_id = parse_int(api_game['id'], 0)
        if game_api_id == 0:
            continue

        # Check for an existing game record
        select_by_id = db.select(Game).where(Game.api_id == game_api_id)
        db_game = Game.get_first(select_by_id)

        if db_game: # Update existing game records
            update_game(api_game, db_game, league)
        elif league and season: # Add new/missing game if we have a league and season
            add_game(api_game, league, subseason) # Added game could be a double-header or extra regular season game added as a playoff

    print("=== pickem === ", "Games scores updated")

def seed_db():
    with scheduler.app.app_context():
        season_start = check_for_league_updates()

        # Get the complete game schedule
        if not app.debug and not app.testing:
            for n in range(1, 240):
                check_for_updates(season_start + timedelta(days=n))
                sleep(1)  # Be nice to the server

def check_for_league_updates():
    """Initialize the database."""
    print("=== pickem === ", "Seeding database...")
    # Fetch a basic scoreboard update from the API to get the sport, league, season info and teams,
    resp_teams = call_espn_api('teams') if not app.testing else get_test_data('espn_teams.json')
    resp_score = call_espn_api('scoreboard') if not app.testing else get_test_data('espn_scoreboard.json')

    sport = resp_teams['sports'][0]
    baseball = Sport.get_first(db.select(Sport).where(Sport.api_id == sport['id']))
    if not baseball:
        baseball = Sport(sport['name'], sport['id'])
        if not baseball.save():
            print("=== pickem ===", baseball, baseball.get_last_error())

    league = sport['leagues'][0]
    mlb = League.get_first(db.select(League).where(League.sport_id == baseball.id and League.name == league['name']))
    if not mlb:
        mlb = League(league['name'], league['abbreviation'], league['id'], baseball.id)
        if not mlb.save():
            print("=== pickem ===", mlb.get_last_error())

    season = resp_score['leagues'][0]['season'] # Season comes from the scoreboard endpoint because is has more detail
    current_season = Season.get_first(db.select(Season).where(Season.league_id == mlb.id and Season.year == season['year']))
    if not current_season:
        current_season = Season(season['displayName'], season['year'], mlb.id)
        if not current_season.save():
            print("=== pickem ===", current_season, current_season.get_last_error())

    season_type = season['type']
    subseason = SubSeason.get_first(db.select(SubSeason).where(SubSeason.season_id == current_season.id and SubSeason.name == season_type['name']))
    if not subseason:
        subseason = SubSeason(season_type['name'], SubSeasonType(season_type['type']), datetime.fromisoformat(season['startDate']), datetime.fromisoformat(season['endDate']), current_season.id)
        if not subseason.save():
            print("=== pickem ===", subseason, subseason.get_last_error())

    # Get the teams for MLB
    for api_team in [team['team'] for team in league['teams']]:
        # Convert some integer values from strings in ESPN's API response
        team_api_id = parse_int(api_team['id'], 0)
        if team_api_id == 0:
            continue

        # Check for an existing team record
        select_by_id = db.select(Team).where(Team.api_id == team_api_id)
        db_team = Team.get_first(select_by_id)

        if db_team: # Update existing team records
            update_team(db_team, api_team)
        else: # Add new/missing team
            add_team(api_team, mlb.id)

    print("=== pickem === ", "Database ready!")
    return subseason.start

def get_test_data(seed_file):
    """Loads test data for tests"""
    return json.load(open(app.instance_path.replace('/instance', '/tests/mock_api_data/') + seed_file))
