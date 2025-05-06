"""
Authentication helper functions and decorators
"""
from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user, login_required

def easy_login_required(f):
    """
    A more user-friendly version of Flask-Login's login_required decorator.
    Redirects to login page with a friendly message instead of 401 error.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('You need to log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function