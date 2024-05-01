import os
import tomllib
from datetime import datetime
from flask import Flask, render_template, session, g
from .extensions import debug_toolbar, scheduler
from .models import db, User
from .forms import SecureEmptyForm
from .blueprints import CURR_USER_KEY
from .api.baseball import check_for_score_updates

def create_app():
    """Initialize the Pickem application."""
    config_file = os.environ.get('APP_TEST_CONFIG', 'config.toml')
    app = Flask(__name__)
    app.config.from_file(f"../{config_file}", load=tomllib.load, text=False)

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
        # check_for_score_updates() # Update scores on startup or seed the database if needed.

        # Register blueprints
        from .blueprints import auth_bp, user_bp
        app.register_blueprint(auth_bp)
        app.register_blueprint(user_bp)
        # app.register_blueprint(message_bp)

        # Home Routes
        @app.get('/')
        def home():
            """Show landing page:
            Anon users: Invite to login/signup
            Logged in user: Invite to make picks or show list of current picks
            """
            if g.user:
                return render_template('home_user.html.jinja', empty_form=SecureEmptyForm())
            else:
                return render_template('home_anon.html.jinja')

        @app.errorhandler(404)
        def show_not_found(e):
            return render_template("errors/404.html.jinja"), 404

        @app.before_request
        def add_user_to_g():
            """If we're logged in, add current user to Flask global."""
            if CURR_USER_KEY in session:
                g.user = User.get(session[CURR_USER_KEY])
            else:
                g.user = None

    return app
