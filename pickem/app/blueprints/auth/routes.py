from flask import request, redirect, render_template, flash, session, url_for, g
from sqlalchemy.exc import IntegrityError
from ...models import db, User
from ...forms import LoginForm, SignupForm
from ..picks import UNSAVED_PICKS_KEY
from ..picks.routes import save_session_picks
from .login import do_login, do_logout
from . import bp

@bp.route('/signup', methods=['GET','POST'])
def signup():
    """Handle user sign up.

    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If the there already is a user with that username: flash message
    and re-present form.
    """
    if g.user:
        return redirect(url_for("home"))

    form = SignupForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data
                # email=form.email.data,
                # image_url=form.image_url.data or User.image_url.default.arg
            )
            db.session.commit()
        except IntegrityError:
            flash(f"Sorry, username @{form.username.data} is already taken.  Did you mean to log in?  Find Login link below.", 'danger')

        if user:
            do_login(user)
            save_session_picks(user)
            return redirect(url_for("home"))

    return render_template('users/signup.html.jinja', form=form)

@bp.route('/login', methods=['GET','POST'])
def login():
    """Handle user login."""
    if g.user:
        return redirect(url_for("home"))

    form = LoginForm()
    form.next.data = request.args.get("next") # If user hit a page while not logged in

    if form.validate_on_submit():
        user = User.authenticate(form.username.data, form.password.data)

        if user:
            do_login(user)
            save_session_picks(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect(form.next.data or url_for("home"))

        flash("Invalid credentials.", 'danger')

    return render_template('users/login.html.jinja', form=form)

@bp.get('/logout')
def logout():
    """Handle logout of user."""
    do_logout()
    flash("You have been logged out.  Thanks for playing!", "success")
    return redirect(url_for("auth.login"))
