import tomllib
from flask import Flask, render_template, redirect, session, url_for, g
from .extensions import debug_toolbar, scheduler, DateConverter
from .models import db, User, Game
from .bp_user import CURRENT_USER_KEY
from .api.baseball import seed_db

def create_app(config_filename = 'config_dev'):
    """Initialize the Pickem application."""
    app = Flask(__name__)
    app.config.from_file(f"../{config_filename}.toml", load=tomllib.load, text=False)
    app.config.from_prefixed_env()
    app.url_map.converters['date'] = DateConverter

    # Set up extensions
    debug_toolbar.init_app(app)
    db.init_app(app)

    if not app.testing: # APScheduler complains the scheduler already started when running all tests
        scheduler.init_app(app)
        scheduler.start()

    with app.app_context():
        db.create_all()

         # Seed the database on first run
        if len(Game.get_all()) == 0:
            seed_db()
 
        # Register blueprints
        from .bp_user import bp as user_bp
        from .bp_game import bp as game_bp
        app.register_blueprint(user_bp)
        app.register_blueprint(game_bp)

        # Home Routes
        @app.get('/')
        def home():
            """Show landing page:
            Anon users: Invite to play the game, then login or signup
            Logged in user: Show current picks and invite to make picks if not done for some games
            """
            if g.user:
                return redirect(url_for('game.my_picks'))
            else:
                return render_template('landing.html.jinja')

        @app.errorhandler(404)
        def show_not_found(e):
            return render_template("errors/404.html.jinja"), 404

        @app.before_request
        def add_user_to_g():
            """If we're logged in, add current user to Flask global."""
            if CURRENT_USER_KEY in session:
                g.user = User.get(session[CURRENT_USER_KEY])
            else:
                g.user = None

    return app
