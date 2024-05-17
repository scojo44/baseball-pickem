import os
import tomllib
from datetime import datetime
from flask import Flask, render_template, redirect, session, url_for, g
from .extensions import debug_toolbar, scheduler, DateConverter
from .models import db, User, Game
from .forms import SecureEmptyForm
from .blueprints.auth import CURRENT_USER_KEY
from .api.baseball import seed_db

def create_app():
    """Initialize the Pickem application."""
    config_file = os.environ.get('APP_TEST_CONFIG', 'config.toml')
    app = Flask(__name__)
    app.config.from_file(f"../{config_file}", load=tomllib.load, text=False)
    app.url_map.converters['date'] = DateConverter

    # Set up extensions
    debug_toolbar.init_app(app)
    db.init_app(app)
    scheduler.init_app(app)
    scheduler.start()

    # Notify on missing API key
    if not os.environ.get('SPORTS_IO_API_KEY'):
        print("Missing API key environment variable!")

    with app.app_context():
        db.create_all()

         # Seed the database on first run
        if len(Game.get_all()) == 0:
            seed_db()
 
        # Register blueprints
        from .blueprints import auth_bp, user_bp, games_bp, picks_bp
        app.register_blueprint(auth_bp)
        app.register_blueprint(user_bp)
        app.register_blueprint(games_bp)
        app.register_blueprint(picks_bp)

        # Home Routes
        @app.get('/')
        def home():
            """Show landing page:
            Anon users: Invite to login/signup
            Logged in user: Invite to make picks or show list of current picks
            """
            if g.user:
                return redirect(url_for('picks.list'))
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
