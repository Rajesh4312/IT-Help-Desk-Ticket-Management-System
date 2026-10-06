from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, User, Ticket
from routes import login_required

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/')
def index():
    """Root redirect based on authentication state and user role."""
    if 'user_id' in session:
        if session.get('user_role') == 'technician':
            return redirect(url_for('technician.dashboard'))
        return redirect(url_for('employee.dashboard'))
    return redirect(url_for('auth.login'))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Employee self-registration."""
    if 'user_id' in session:
        return redirect(url_for('auth.index'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Server-side validation
        if not name or not email or not password or not confirm_password:
            flash('All fields are required.', 'danger')
            return render_template('register.html', name=name, email=email)

        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template('register.html', name=name, email=email)

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html', name=name, email=email)

        # Check existing user
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('An account with this email address already exists. Please log in.', 'warning')
            return redirect(url_for('auth.login'))

        # Create new employee user
        user = User(name=name, email=email, role='employee')
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash('Registration successful! You may now log in to submit IT tickets.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Authenticate users with email and password."""
    if 'user_id' in session:
        return redirect(url_for('auth.index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        next_page = request.form.get('next') or request.args.get('next')

        if not email or not password:
            flash('Please enter both email and password.', 'danger')
            return render_template('login.html', email=email)

        user = User.query.filter_by(email=email).first()

        if user is None or not user.check_password(password):
            flash('Invalid email or password. Please verify your credentials.', 'danger')
            return render_template('login.html', email=email)

        # Session initialization
        session.clear()
        session['user_id'] = user.id
        session['user_name'] = user.name
        session['user_email'] = user.email
        session['user_role'] = user.role

        flash(f'Welcome back, {user.name}!', 'success')

        # Handle safe redirect
        if next_page and next_page.startswith('/') and not next_page.startswith('//'):
            # Ensure technician pages are only navigated to if technician
            if next_page.startswith('/technician') and user.role != 'technician':
                return redirect(url_for('employee.dashboard'))
            if next_page.startswith('/employee') and user.role != 'employee':
                return redirect(url_for('technician.dashboard'))
            return redirect(next_page)

        if user.role == 'technician':
            return redirect(url_for('technician.dashboard'))
        return redirect(url_for('employee.dashboard'))

    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    """Clear session data and log out the user."""
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/profile')
@login_required
def profile():
    """Display user profile summary and activity."""
    user = db.session.get(User, session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('auth.login'))

    stats = {}
    if user.is_employee():
        stats['total_tickets'] = user.created_tickets.count()
        stats['open_tickets'] = user.created_tickets.filter_by(status='Open').count()
        stats['resolved_tickets'] = user.created_tickets.filter_by(status='Resolved').count()
    else:
        stats['assigned_tickets'] = user.assigned_tickets.count()
        stats['active_tickets'] = user.assigned_tickets.filter(Ticket.status.in_(['Open', 'In Progress'])).count()

    return render_template('profile.html', user=user, stats=stats)
