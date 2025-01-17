"""Routes for game pages."""
import json
import sqlalchemy
from datetime import datetime, date, timedelta, timezone
from flask import current_app as app, redirect, render_template, session, flash, url_for, g
from ..api.baseball import check_for_updates
from ..models import db, User, Team, Game, GameStatus, Pick
from ..forms import GamePickForm
from ..bp_user.routes import login_required, admin_login_required
from . import bp, UNSAVED_PICKS_KEY

######################################################
# My Picks
@bp.get('/mypicks')
@login_required
def my_picks():
    """List user's picks."""
    # Save picks from session if the user just made them and logged in or signed up.
    save_session_picks(g.user)

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
        game_count_select = db.select(sqlalchemy.func.count()).select_from(Game).where(Game.start_time.between(datetime.now(timezone.utc), today + two_days))
        game_count = db.session.scalar(game_count_select)
        # Tally the user's picks for games that haven't started yet
        user_picks = [p for p in g.user.picks if p.game.start_time > datetime.now(timezone.utc)]
        need_button = len(user_picks) < game_count

    return render_template('games/mypicks.html.jinja', dates=dates, need_make_picks_button=need_button)

######################################################
# Pick Sheet
@bp.route('/picksheet', methods=['GET', 'POST'])
def picksheet():
    """Get the list of games to pick"""
    form = GamePickForm()

    # Temporarily record the picks on the session until the user logs in or signs up.
    if form.validate_on_submit():
        picks = json.loads(form.picks.data)

        if g.user:
            save_session_picks(g.user, picks)
            flash('Great picks!  Check back later to see how you did.', 'success')
            return redirect(url_for('game.my_picks'))
        else:
            session[UNSAVED_PICKS_KEY] = picks
            flash('Great picks!  Log in or sign up to save them and see how you did after some games are played.', 'success')
            return redirect(url_for('user.signup'))

    return render_template('games/picksheet.html.jinja', form=form)

@bp.get('/picksheet/games')
def picksheet_games():
    """Get the games to pick as JSON."""
    today = date.today()
    tomorrow = today + timedelta(days=1)
    one_day = timedelta(days=1)

    # Load games from today and tomorrow
    select_today = db.select(Game).where(Game.start_time.between(today, tomorrow)).where(Game.status == GameStatus.NS).order_by(Game.start_time)
    select_tomorrow = db.select(Game).where(Game.start_time.between(tomorrow, tomorrow + one_day)).order_by(Game.start_time)
    today_games = Game.get_all(select_today)
    tomorrow_games = Game.get_all(select_tomorrow)

    # Filter out games the user already picked
    if g.user:
        picked_games = [p.game for p in g.user.picks]
        today_games = [game for game in today_games if game not in picked_games]
        tomorrow_games = [game for game in tomorrow_games if game not in picked_games]

    return {'gamesToPick': [
        {
            'date': today.strftime("%A, %B %-d"),
            'games': [game.as_dict() for game in today_games]
        },
        {
            'date': tomorrow.strftime("%A, %B %-d"),
            'games': [game.as_dict() for game in tomorrow_games]
        }
    ]}

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

        # Ignore if the game has already started
        if game.start_time < datetime.now(timezone.utc):
            continue

        # Record the pick
        pick = Pick(user.id, game.id, team.id)
        if not pick.save():
            print(pick.get_last_error())

        if session.get(UNSAVED_PICKS_KEY):
            del session[UNSAVED_PICKS_KEY]

######################################################
# Edit Picks (might use this later)
# @bp.post('/picks/edit')
def edit_pick():
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

######################################################
# Scoreboard
@bp.get('/scoreboard')
@login_required
def scoreboard():
    """Show the current game scores"""
    # Get all the games for the given day
    one_day = timedelta(days=1)
    today = date.today()
    next = str(today + one_day)
    prev = str(today - one_day)
    return render_template('games/scoreboard.html.jinja', today=today, next_day=next, prev_day=prev)

@bp.get('/scoreboard/games')
@bp.get('/scoreboard/games/<date:day>')
@login_required
def scoreboard_by_date(day = date.today()):
    """Show the current game scores"""
    # Get all the games for the given day
    one_day = timedelta(days=1)
    select = db.select(Game).where(Game.start_time.between(day, day + one_day)).order_by(Game.start_time)
    games = [g.as_dict() for g in Game.get_all(select)]
    picks = {}
    points = None

    if g.user:
        picks = [p.as_dict() for p in g.user.picks]
        points = len([p for p in g.user.picks if p.is_correct and p.game.start_time.date() == day])

    for game in games:
        game['pick'] = next((p for p in picks if p['gameID'] == game['id']), None)

    return {
        'games': games,
        'dayDisplay': day.strftime("%a, %B %-d"),
        'day': str(day),
        'nextDay': str(day + one_day),
        'prevDay': str(day - one_day),
        'userPoints': points
    }

@bp.get('/scoreboard/update')
@admin_login_required
def scoreboard_full_update():
    """Force an update of all games"""
    if not app.testing: # Skip API call and just make sure admin rights are required
        check_for_updates(None)

    return redirect(url_for('game.scoreboard'))

######################################################
# Leadaerboard
@bp.get('/leaderboard')
@login_required
def leaderboard():
    """Show the users with the most correct picks for all season and today."""
    one_day = timedelta(days=1)
    today = date.today()
    next = str(today + one_day)
    prev = str(today - one_day)
    return render_template('games/leaderboard.html.jinja', season_leaders=get_leaders(), today=today, next_day=next, prev_day=prev)

@bp.get('/leaderboard/users')
@bp.get('/leaderboard/users/<date:day>')
@login_required
def leaderboard_by_date(day = date.today()):
    """Show the users with the most correct picks among games played on the given date."""
    one_day = timedelta(days=1)
    leaders = get_leaders(lambda pick_day: pick_day == day)

    # Sort leaders by most points first
    leaders.sort(reverse=True, key=lambda u: u['points'])

    return {
        'users': leaders,
        'dayDisplay': day.strftime("%a, %B %-d"),
        'day': str(day),
        'nextDay': str(day + one_day),
        'prevDay': str(day - one_day)
    }

def get_leaders(date_filter = lambda pick_day: True):
    """Return a dict of users and points.
    
    filter: An optional function that checks the game date of the pick."""
    leaders = []

    for user in User.get_all():
        correct_picks = [p for p in user.picks if p.is_correct and date_filter(p.game.start_time.date())]

        leaders.append({
            'name': user.username,
            'points': len(correct_picks)
        })

    leaders.sort(key=lambda user: user['points'], reverse=True)
    return leaders
