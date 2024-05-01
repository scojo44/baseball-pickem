"""Baseball API updates provided by api-sports.io"""
import os
from datetime import datetime, date, timedelta
import requests
from ..extensions import scheduler
from ..models import db, Sport, League, Team, Season, SubSeason, SubSeasonType, Game

# Get an API key at https://api-sports.io
# No credit card required for free tier (as of April 23, 2024)
API_SPORTS_IO_PREFIX = 'https://v1.baseball.api-sports.io/'

def seed_db():
    """Initialize the database with the complete game schedule."""
    # Hardcode the sport and league
    print("=== pickem === ", "Loading sports, leagues, seasons...")
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
        print("=== pickem === ", "Loading teams from API...")
        teams = call_sports_io_api('teams', api_params)
    except Exception as e:
        handle_api_errors(e)
        return

    for team in teams:
        Team(team['name'], team['id'], league.id).save()

    # Get the games for MLB
    try:
        print("=== pickem === ", "Loading games from API...")
        games = call_sports_io_api('games', api_params)
    except Exception as e:
        handle_api_errors(e)
        return

    for game in games:
        add_game(game, subseason.id)

def call_sports_io_api(endpoint: str, params: dict = {}) -> dict:
    """Call the Sports.io API.  params is a dict containing query string parameters"""
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

def handle_api_errors(error):
    """Handle errors returned from the API."""
    print(error)

def add_game(api_game: dict, subseason_id: int) -> None:
    """Save a game to the database."""
    select_hteam = db.select(Team).where(Team.api_id == api_game['teams']['home']['id'])
    select_ateam = db.select(Team).where(Team.api_id == api_game['teams']['away']['id'])

    new_game = Game(
        start = datetime.fromisoformat(api_game['date']),
        home_team_id = Team.get_first(select_hteam).id,
        away_team_id = Team.get_first(select_ateam).id,
        api_id = api_game['id'],
        subseason_id = subseason_id,
        status = api_game['status']['short'],
        home_score = api_game['scores']['home']['total'],
        away_score = api_game['scores']['home']['total']
    )

    if not new_game.save():
        print("=== pickem ===", new_game.last_error)

def update_game(db_game: Game, api_game: dict):
    """Update a game in the database."""
    # Update the scores
    db_game.status = api_game['status']['short']
    db_game.home_score = api_game['scores']['home']['total']
    db_game.away_score = api_game['scores']['away']['total']
    # Time could change for doubleheaders and TV network demands
    db_game.start = datetime.fromisoformat(api_game['date'])
    # These shouldn't change but update them just in case
    select_hteam = db.select(Team).where(Team.api_id == api_game['teams']['home']['id'])
    select_ateam = db.select(Team).where(Team.api_id == api_game['teams']['away']['id'])
    db_game.home_team = Team.get_first(select_hteam)
    db_game.away_team = Team.get_first(select_ateam)

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
    # Seed the database on first run
    if len(Game.get_all()) == 0:
        seed_db()
        return # Wait until the next run to check for updates

    print("=== pickem === ", "Updating games from API...")

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
