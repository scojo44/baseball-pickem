from flask import request, redirect, render_template, flash, url_for, g
from ...models import db, User
from ...forms import UserProfileForm, SecureEmptyForm
from ..auth.login import login_required, do_logout
from . import bp

@bp.get('/users')
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

@bp.get('/users/<int:user_id>')
def show(user_id):
    """Show user profile."""
    user = User.get_or_404(user_id)

    # snagging messages in order from the database;
    # user.messages won't be in order by default
    # select = db.select(Message).where(Message.user_id == user_id).order_by(Message.timestamp.desc()).limit(100)
    # messages = Message.get_all(select)
    return render_template('users/show.html.jinja', user=user, empty_form=SecureEmptyForm())

@bp.route('/users/profile', methods=["GET", "POST"])
@login_required
def profile():
    """Update profile for current user."""
    form = UserProfileForm(obj=g.user)

    if form.validate_on_submit():
        if User.authenticate(g.user.username, form.password.data):
            username_changed = g.user.username != form.username.data
            g.user.username = form.username.data
            g.user.email = form.email.data
            g.user.bio = form.bio.data
            g.user.location = form.location.data
            g.user.image_url = form.image_url.data
            g.user.header_image_url = form.header_image_url.data
            db.session.add(g.user)
            db.session.commit()
            flash("Your profile was updated.", "success")

            if username_changed:
                flash("Since you changed your username, we logged you off so you can log back in with your new username.", "info")
                do_logout()
                return redirect(url_for("auth.login"))

            return redirect(url_for("user.messages", user_id=g.user.id))

        flash("Invalid credentials.", 'danger')
        return redirect(url_for("home"))

    return render_template('users/edit.html.jinja', form=form)

@bp.post('/users/delete')
@login_required
def delete():
    """Delete user."""
    if SecureEmptyForm().validate_on_submit():
        do_logout()
        db.session.delete(g.user)
        db.session.commit()
        flash("Your account and any warbles have been deleted.", "danger")
        return redirect(url_for("auth.signup"))

    return redirect(request.referrer or url_for("user.profile"))
