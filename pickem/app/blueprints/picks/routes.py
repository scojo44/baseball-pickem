from datetime import datetime, date, timedelta
from flask import render_template, session, g
from sqlalchemy import func
from ...models import db, User, Game, Team, Pick
from ...forms import GamePickForm
from ..auth.login import login_required
from . import bp, UNSAVED_PICKS_KEY

@bp.get('')
@login_required
def list():
    """List user's picks."""
    dates = {}
    picks = g.user.picks

    # Make a list of dates with games the user picked
    for p in picks:
        day = p.game.start_time.date()
        dates[str(day)] = {
            'date_heading': day.strftime("%B %-d, %Y")
        }

    # Add the points (number of correct picks) to the day
    for day in dates.keys():
        dates[day]['points'] = len([p for p in g.user.picks if p.is_correct and day == str(p.game.start_time.date())])

    picks_by_date = {}
    picks = g.user.picks

    # Group picks by day in a dictionary of lists
    for p in picks:
        day = p.game.start_time.date()
        key = str(day)

        if not picks_by_date.get(key):
            picks_by_date[key] = []

        picks_by_date[key].append(p.as_dict())


    # See if the user needs to make picks for tomorrow's games
    today = date.today()
    tomorrow = today + timedelta(days=1)
    two_days = timedelta(days=2)
    need_button = dates.get(str(tomorrow)) == None # Tomorrow didn't appear in the above date scan so we know to show the button.  Skip next check.

    # Check if the user made a pick for all the available games
    if not need_button:
        # See how many games are available to pick
        game_count_select = db.select(func.count()).select_from(Game).where(Game.start_time.between(datetime.now(), today + two_days))
        game_count = db.session.scalar(game_count_select)
        # Tally the user's picks for games that haven't started yet
        user_picks = [p for p in g.user.picks if p.game.start_time > datetime.now()]
        need_button = len(user_picks) < game_count

    return render_template('games/mypicks.html.jinja', dates=dates, need_make_picks_button=need_button)

@bp.post('/edit')
def edit():
    """Accept a pick to be changed.  TODO: change to edit function."""
    form = GamePickForm()
    result = False

    # Temporarily record the picks on the session until the user logs in or signs up.
    if form.validate_on_submit():
        picks = session.get(UNSAVED_PICKS_KEY, [])
        picks.append({'game': form.game_id.data, 'team': form.team_id.data})
        session[UNSAVED_PICKS_KEY] = picks
        result = True

    return {'result': result}

def save_session_picks(user, picks = None):
    """After user logged in or signed up, save the picks passed in or from the session."""
    # Process picks from session if no picks passed in.  Or do nothing if session picks is an empty list.
    for p in picks or session.get(UNSAVED_PICKS_KEY, []):
        game_id = p['game']
        team_id = p['team']

        # Check for an existing pick from the user and don't change it.
        select = db.select(Pick).where(Pick.user_id == user.id).where(Pick.game_id == game_id)
        if Pick.get_first(select) is not None:
            continue

        game: Game = Game.get(game_id)
        team: Team = Team.get(team_id)

        # Ignore invalid game or team
        if not game or not team:
            continue
        # Ignore if team not playing in the game
        elif team.id not in [game.home_team_id, game.away_team_id]:
            continue

        # Record the pick
        pick = Pick(user.id, game.id, team.id)
        if pick.save():
            print(pick.get_last_error())

        if session.get(UNSAVED_PICKS_KEY):
            del session[UNSAVED_PICKS_KEY]