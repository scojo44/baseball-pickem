import json
from datetime import date, timedelta
from flask import request, redirect, render_template, flash, session, url_for, g
from ...models import db, Game, GameStatus, User, Pick
from ...forms import GamePickForm
from ..auth.login import login_required
from ..picks.routes import save_session_picks
from . import bp, UNSAVED_PICKS_KEY

@bp.route('/picksheet', methods=['GET', 'POST'])
def picksheet():
    """Get the list of games to pick"""
    # Today's games that haven't started yet
    form = GamePickForm()

    # Temporarily record the picks on the session until the user logs in or signs up.
    if form.validate_on_submit():
        picks = json.loads(form.picks.data)

        if g.user:
            save_session_picks(g.user, picks)
            return redirect(url_for('home'))
        else:
            session[UNSAVED_PICKS_KEY] = picks
            return redirect(url_for('auth.signup'))

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

    return leaders
