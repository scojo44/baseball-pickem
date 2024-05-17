import functools
from flask import request, redirect, flash, url_for, session, g
from . import CURRENT_USER_KEY

def login_required(f):
    """Decorator for routes that requre a logged in user."""
    @functools.wraps(f)
    def view_requiring_login(*args, **kwargs):
        if not g.user:
            flash("Access unauthorized.  Please log in first.", "danger")
            return redirect(url_for("auth.login", next=request.path))
        return f(*args, **kwargs)
    
    return view_requiring_login

def do_login(user):
    """Log in user."""
    session[CURRENT_USER_KEY] = user.id

def do_logout():
    """Logout user."""
    if CURRENT_USER_KEY in session:
        del session[CURRENT_USER_KEY]
