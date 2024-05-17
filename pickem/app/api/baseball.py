"""Baseball API updates provided by api-sports.io"""
import os
from datetime import datetime, date, timedelta
import requests
from ..extensions import scheduler
from ..models import db, Sport, League, Team, Season, SubSeason, SubSeasonType, Game

# Get an API key at https://api-sports.io
# No credit card required for free tier (as of April 23, 2024)
API_SPORTS_IO_PREFIX = 'https://v1.baseball.api-sports.io/'
API_ESPN_PREFIX = 'http://site.api.espn.com/apis/site/v2/sports/baseball/mlb/'

def call_sports_io_api(endpoint: str, params: dict = {}) -> dict:
    """Call the Sports.io API.  params is a dict containing query string parameters."""
    try:
        headers = {'X-APISports-Key': os.environ.get('SPORTS_IO_API_KEY')}
        resp = requests.get(API_SPORTS_IO_PREFIX + endpoint, headers=headers, params=params)
        json = resp.json()

        # Check for errors
        if json['errors']:
            raise Exception("Error callig API: " + str(json['errors']))

        # The data is in the response object
        return json['response']

    except(requests.ConnectionError, requests.Timeout, requests.TooManyRedirects, requests.JSONDecodeError):
        return None  # Ignore the error and signal by returning None

def call_espn_teams_api() -> dict:
    """Call the ESPN API."""
    try:
        resp = requests.get(API_ESPN_PREFIX + 'teams')
        json = resp.json()
        teams = []
        for team in json['sports'][0]['leagues'][0]['teams']:
            teams.append(team['team'])
        return teams

    except(requests.ConnectionError, requests.Timeout, requests.TooManyRedirects, requests.JSONDecodeError):
        return None  # Ignore the error and signal by returning None

def handle_api_errors(error):
    """Handle errors returned from the API."""
    print(error)

def add_game(api_game: dict, subseason_id: int) -> None:
    """Save a game to the database."""
    select_hteam = db.select(Team).where(Team.api_id == api_game['teams']['home']['id'])
    select_ateam = db.select(Team).where(Team.api_id == api_game['teams']['away']['id'])

    new_game = Game(
        start = datetime.fromisoformat(api_game['date']),
        away_team_id = Team.get_first(select_ateam).id,
        home_team_id = Team.get_first(select_hteam).id,
        api_id = api_game['id'],
        subseason_id = subseason_id,
        status = api_game['status']['short'],
        away_score = api_game['scores']['away']['total'],
        home_score = api_game['scores']['home']['total'],
        away_hits = api_game['scores']['away']['hits'],
        home_hits = api_game['scores']['home']['hits'],
        away_errors = api_game['scores']['away']['errors'],
        home_errors = api_game['scores']['home']['errors']
    )

    if not new_game.save():
        print("=== pickem ===", new_game.last_error)

def update_game(db_game: Game, api_game: dict):
    """Update a game in the database."""
    # Update the scores
    db_game.status = api_game['status']['short']
    db_game.away_score = api_game['scores']['away']['total']
    db_game.home_score = api_game['scores']['home']['total']
    db_game.away_hits = api_game['scores']['away']['hits']
    db_game.home_hits = api_game['scores']['home']['hits']
    db_game.away_errors = api_game['scores']['away']['errors']
    db_game.home_errors = api_game['scores']['home']['errors']
    # Start time could change for doubleheaders and TV network demands
    db_game.start = datetime.fromisoformat(api_game['date'])
    # These shouldn't change but update them just in case
    select_ateam = db.select(Team).where(Team.api_id == api_game['teams']['away']['id'])
    select_hteam = db.select(Team).where(Team.api_id == api_game['teams']['home']['id'])
    db_game.away_team = Team.get_first(select_ateam)
    db_game.home_team = Team.get_first(select_hteam)

    if not db_game.save():
        print("=== pickem ===", db_game.last_error)

# These three functions are called by the scheduler.  Jobs are defined in the config file.
def check_for_game_updates(): # Runs once per day
    """Check for game schedule updates."""
    with scheduler.app.app_context(): # Get game schedule updates two days out
        check_for_updates(datetime.now().date() + timedelta(days=1), 1, SubSeason.get(1))

def check_for_late_game_scores(): # Runs once per day
    """Check scores for yesterday's late games."""
    with scheduler.app.app_context():
        check_for_updates(datetime.now().date() - timedelta(days=1), 1, SubSeason.get(1))

def check_for_score_updates(): # Runs every twenty minutes
    """Check for the latest game scores."""
    with scheduler.app.app_context():
        check_for_updates(datetime.now().date(), 1, SubSeason.get(1))

def check_for_updates(day: date, league_id: int, subseason: SubSeason) -> None:
    """Update game records with current scores, changed start times.
    Add games that were not on the original schedule.
    Delete games that no longer exist."""
    print("=== pickem === ", "Updating game scores from API...")

    api_params = {
        'date': day.isoformat(),
        'league': league_id,
        'season': subseason.season.year
    }

    # Get the day's games from the API
    try:
        api_games = call_sports_io_api('games', api_params)
    except Exception as e:
        handle_api_errors(e)
        return

    # Get the day's games from the database
    select_by_day = db.select(Game).where(Game.start_time.between(day, day + timedelta(days=1)))
    saved_games: list[Game] = Game.get_all(select_by_day)

    # Remove games in the database that no longer exist
    for db_game in saved_games:
        game_scheduled = False

        for api_game in api_games:
            if api_game['id'] == db_game.api_id:
                game_scheduled = True

        if not game_scheduled:
            db_game.delete()

    # Check for game updates and games that were added after seeding
    for api_game in api_games:
        # Check for an existing game record
        select_by_id = db.select(Game).where(Game.api_id == api_game['id'])
        db_game = Game.get_first(select_by_id)

        if db_game: # Update existing game records
            update_game(db_game, api_game)
        else: # Add new/missing game
            add_game(api_game, 1) # Could be a double-header or extra regular season game added as a playoff

    print("=== pickem === ", "Games scores updated")

def seed_db():
    """Initialize the database with the complete game schedule."""
    print("=== pickem === ", "Seeding database...")
    # Hardcode the sport and league
    baseball = Sport('Baseball')
    if not baseball.save():
        print("=== pickem ===", baseball.last_error)

    league = League('Major League Baseball', 'MLB', 1, baseball.id)
    if not league.save():
        print("=== pickem ===", league.last_error)

    # Hard-code the seasons for now
    season = Season('2024', 2024, league.id)
    if not season.save():
        print("=== pickem ===", season.last_error)
    subseason = SubSeason('Regular Season', SubSeasonType.regular, datetime(2024, 3, 28), datetime(2024, 10, 1), season.id)
    if not subseason.save():
        print("=== pickem ===", subseason.last_error)

    api_params = {
        'league': 1,
        'season': datetime.now().year
    }

    # Get the teams for MLB
    try:
        asio_teams = call_sports_io_api('teams', api_params) or []
    except Exception as e:
        handle_api_errors(e)
        return
    
    espn_teams = call_espn_teams_api() or []
    if not espn_teams:
        return

    # Team names from all-sports.io that need fixed as of May 7, 2024
    #9: Cleveland Indians is now the Guardians
    #33: St. Louis Cardinals is missing a space, 'St.Louis Cardinals'

    for et in espn_teams:
        # Find the all-sports.io team ID for this ESPN team by searching for the team name.
        asio_team_id = [t for t in asio_teams if et['name'] in t['name'] or t['name'] == f"{et['location']} Indians"][0]['id']
        team = Team(et['name'], et['location'], et['abbreviation'], et['logos'][0]['href'], asio_team_id, league.id)
        if not team.save():
            print(team, team.get_last_error())

    # Add All-Star teams
    al = Team('American League', '', 'AL', 'https://a.espncdn.com/i/teamlogos/mlb/500/al.png', 1, league.id)
    if not al.save():
        print(al, al.get_last_error())
    nl = Team('National League', '', 'NL', 'https://a.espncdn.com/i/teamlogos/mlb/500/nl.png', 23, league.id)
    if not nl.save():
        print(nl, nl.get_last_error())

    # Get the games for MLB
    try:
        games = call_sports_io_api('games', api_params) or []
    except Exception as e:
        handle_api_errors(e)
        return

    for game in games:
        add_game(game, subseason.id)

    print("=== pickem === ", "Database ready!")
