from functools import wraps
from flask import session, redirect, url_for, flash, abort, request


def login_required(view):
    """Ensure that the user is logged into the application."""
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login', next=request.path))
        return view(*args, **kwargs)
    return wrapped_view


def technician_required(view):
    """Ensure that the logged-in user has the technician role."""
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login', next=request.path))
        if session.get('user_role') != 'technician':
            abort(403)
        return view(*args, **kwargs)
    return wrapped_view


def employee_required(view):
    """Ensure that the logged-in user has the employee role."""
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login', next=request.path))
        if session.get('user_role') != 'employee':
            abort(403)
        return view(*args, **kwargs)
    return wrapped_view
