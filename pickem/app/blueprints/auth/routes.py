from flask import request, redirect, render_template, flash, url_for, g
from sqlalchemy.exc import IntegrityError
from ...models import db, User
from ...forms import UserAddForm, LoginForm
from ..login import do_login, do_logout
from . import bp

@bp.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.

    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If the there already is a user with that username: flash message
    and re-present form.
    """
    if g.user:
        return redirect(url_for("home"))

    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
                image_url=form.image_url.data or User.image_url.default.arg
            )
            db.session.commit()
        except IntegrityError:
            flash(f"Sorry, username @{form.username.data} is already taken.", 'danger')
            return render_template('users/signup.html.jinja', form=form)

        do_login(user)
        return redirect(url_for("home"))
    else:
        return render_template('users/signup.html.jinja', form=form)

@bp.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""
    if g.user:
        return redirect(url_for("home"))

    # Save the URL if the user tried to access a page while not logged in.
    form = LoginForm()
    form.next.data = request.args.get("next")

    if form.validate_on_submit():
        user = User.authenticate(form.username.data, form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect(form.next.data or url_for("home"))

        flash("Invalid credentials.", 'danger')

    return render_template('users/login.html.jinja', form=form)

@bp.get('/logout')
def logout():
    """Handle logout of user."""
    do_logout()
    flash("You have been logged out.  Thanks for coming!", "success")
    return redirect(url_for("auth.login"))
