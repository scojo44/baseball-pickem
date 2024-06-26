"""Routes for user pages."""
import functools
from sqlalchemy.exc import IntegrityError
from flask import request, redirect, render_template, flash, session, url_for, g
from ..models import db, User
from ..forms import SignupForm, LoginForm, UserProfileForm, ChangePasswordForm, SecureEmptyForm
from . import bp, CURRENT_USER_KEY

def login_required(f):
    """Decorator for routes that requre a logged in user."""
    @functools.wraps(f)
    def view_requiring_login(*args, **kwargs):
        if not g.user:
            flash("Access unauthorized.  Please log in first.", "error")
            return redirect(url_for("user.login", next=request.path))
        return f(*args, **kwargs)
    
    return view_requiring_login

def do_login(user):
    """Log in user."""
    session[CURRENT_USER_KEY] = user.id

def do_logout():
    """Logout user."""
    if CURRENT_USER_KEY in session:
        del session[CURRENT_USER_KEY]

@bp.route('/signup', methods=['GET','POST'])
def signup():
    """Handle user sign up.

    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If the there already is a user with that username: flash message
    and re-present form.
    """
    if g.user:
        return redirect(url_for("game.my_picks"))

    form = SignupForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                # email=form.email.data,
                image_url=form.image_url.data or None
            )
            db.session.commit()
            do_login(user)
            flash(f"Welcome, {user.username}, your picks are here!", "success")
            return redirect(url_for("game.my_picks"))

        except IntegrityError:
            db.session.rollback()
            flash(f"Sorry, username {form.username.data} is already taken.  Did you mean to log in?  Log in with the link below.", 'error')

    return render_template('users/signup.html.jinja', form=form)

@bp.route('/login', methods=['GET','POST'])
def login():
    """Handle user login."""
    if g.user:
        return redirect(url_for("game.my_picks"))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data, form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect(form.next.data or url_for("game.my_picks"))

        flash("Invalid credentials.", 'error')

    form.next.data = request.args.get("next") # If user hit a page while not logged in
    return render_template('users/login.html.jinja', form=form)

@bp.get('/logout')
def logout():
    """Handle logout of user."""
    if g.user:
        do_logout()
        flash("You have been logged out.  Thanks for playing!", "success")

    return redirect(url_for('home'))

@bp.get('/users')
@login_required
def list():
    """Page with listing of users.

    Can take a 'q' param in querystring to search by that username.
    """
    search = request.args.get('q')
    select = None

    if search:
        select = db.select(User).where(User.username.like(f"%{search}%"))

    users = User.get_all(select)
    return render_template('users/list.html.jinja', users=users, empty_form=SecureEmptyForm())

@bp.route('/users/profile', methods=["GET", "POST"])
@login_required
def profile():
    """Update profile for current user."""
    form = UserProfileForm(obj=g.user)

    if form.validate_on_submit():
        if User.authenticate(g.user.username, form.password.data):
            username_changed = g.user.username != form.username.data
            g.user.username = form.username.data
            # g.user.email = form.email.data
            g.user.image_url = form.image_url.data

            if not g.user.save():
                flash("Error saving your profile changes.")
                print("=== pickem ===", g.user.get_last_error())

            flash("Your profile was updated.", "success")

            if username_changed:
                flash("Since you changed your username, we logged you off so you can log back in with your new username: " + g.user.username, "info")
                do_logout()
                return redirect(url_for('user.login'))

            return redirect(url_for("game.my_picks"))

        flash("Invalid credentials.", 'error')

    return render_template('users/profile.html.jinja', form=form)

@bp.route('/users/password', methods=["GET", "POST"])
@login_required
def change_password():
    """Place for users to change their password."""
    form = ChangePasswordForm()

    # Save the new password if the old password was correct
    if form.validate_on_submit():
        if User.authenticate(g.user.username, form.password.data):
            g.user.change_password(form.new_password.data)

            if not g.user.save():
                flash("Error changing your password.  Be sure to test the old and new passwords to find out which one works.")
                print("=== pickem ===", g.user.get_last_error())

            flash("Your password was changed.  Remember to update your password manager.", "success")
            return redirect(url_for("game.my_picks"))

        flash("Invalid credentials.", 'error')

    return render_template('users/password.html.jinja', form=form)

@bp.post('/users/delete')
@login_required
def delete():
    """Delete user."""
    if SecureEmptyForm().validate_on_submit():
        do_logout()

        if not g.user.delete():
            flash("Error deleting your account.")
            print("=== pickem ===", g.user.get_last_error())

        flash("Your account has been deleted.", "error")
        return redirect(url_for('home'))

    return redirect(request.referrer or url_for("user.profile"))
