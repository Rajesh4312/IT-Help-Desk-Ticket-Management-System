from datetime import datetime, timezone
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, abort, current_app
from models import db, Ticket, TicketComment
from routes import employee_required

employee_bp = Blueprint('employee', __name__, url_prefix='/employee')


@employee_bp.route('/dashboard')
@employee_required
def dashboard():
    """Employee personal dashboard with ticket counts and recent issues."""
    user_id = session['user_id']

    # Aggregated metric counts for the logged-in employee
    total_tickets = Ticket.query.filter_by(employee_id=user_id).count()
    open_tickets = Ticket.query.filter_by(employee_id=user_id, status='Open').count()
    in_progress_tickets = Ticket.query.filter_by(employee_id=user_id, status='In Progress').count()
    resolved_tickets = Ticket.query.filter_by(employee_id=user_id, status='Resolved').count()
    closed_tickets = Ticket.query.filter_by(employee_id=user_id, status='Closed').count()

    # Recent tickets for the dashboard table
    recent_tickets = (
        Ticket.query.filter_by(employee_id=user_id)
        .order_by(Ticket.created_at.desc())
        .limit(5)
        .all()
    )

    metrics = {
        'total': total_tickets,
        'open': open_tickets,
        'in_progress': in_progress_tickets,
        'resolved': resolved_tickets,
        'closed': closed_tickets
    }

    return render_template(
        'employee/dashboard.html',
        metrics=metrics,
        recent_tickets=recent_tickets
    )


@employee_bp.route('/tickets')
@employee_required
def tickets():
    """List all tickets submitted by the logged-in employee with optional status filtering."""
    user_id = session['user_id']
    status_filter = request.args.get('status', '').strip()
    category_filter = request.args.get('category', '').strip()

    query = Ticket.query.filter_by(employee_id=user_id)

    if status_filter and status_filter in current_app.config['STATUSES']:
        query = query.filter_by(status=status_filter)

    if category_filter and category_filter in current_app.config['CATEGORIES']:
        query = query.filter_by(category=category_filter)

    employee_tickets = query.order_by(Ticket.created_at.desc()).all()

    return render_template(
        'employee/tickets.html',
        tickets=employee_tickets,
        selected_status=status_filter,
        selected_category=category_filter,
        categories=current_app.config['CATEGORIES'],
        statuses=current_app.config['STATUSES']
    )


@employee_bp.route('/tickets/create', methods=['GET', 'POST'])
@employee_required
def create_ticket():
    """Create a new technical support ticket."""
    categories = current_app.config['CATEGORIES']
    priorities = current_app.config['PRIORITIES']

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        category = request.form.get('category', '').strip()
        priority = request.form.get('priority', '').strip()

        # Validate required fields
        if not title:
            flash('Problem title is required.', 'danger')
            return render_template('employee/create_ticket.html', categories=categories, priorities=priorities, form_data=request.form)

        if not description:
            flash('Problem description is required.', 'danger')
            return render_template('employee/create_ticket.html', categories=categories, priorities=priorities, form_data=request.form)

        if category not in categories:
            flash('Please select a valid problem category.', 'danger')
            return render_template('employee/create_ticket.html', categories=categories, priorities=priorities, form_data=request.form)

        if priority not in priorities:
            flash('Please select a valid priority level.', 'danger')
            return render_template('employee/create_ticket.html', categories=categories, priorities=priorities, form_data=request.form)

        # Create ticket record
        ticket = Ticket(
            title=title,
            description=description,
            category=category,
            priority=priority,
            status='Open',
            employee_id=session['user_id']
        )
        db.session.add(ticket)
        db.session.commit()

        flash(f'Ticket #{ticket.id} created successfully! Our IT team has been notified.', 'success')
        return redirect(url_for('employee.ticket_detail', ticket_id=ticket.id))

    return render_template('employee/create_ticket.html', categories=categories, priorities=priorities, form_data={})


@employee_bp.route('/tickets/<int:ticket_id>')
@employee_required
def ticket_detail(ticket_id):
    """View details of a specific ticket. Enforces employee ownership."""
    ticket = db.session.get(Ticket, ticket_id)
    if not ticket:
        abort(404)

    # Strictly prevent viewing other employees' tickets
    if ticket.employee_id != session['user_id']:
        abort(403)

    return render_template('employee/ticket_detail.html', ticket=ticket)


@employee_bp.route('/tickets/<int:ticket_id>/comment', methods=['POST'])
@employee_required
def add_comment(ticket_id):
    """Add an employee reply or additional info to an existing ticket."""
    ticket = db.session.get(Ticket, ticket_id)
    if not ticket:
        abort(404)

    if ticket.employee_id != session['user_id']:
        abort(403)

    comment_text = request.form.get('comment', '').strip()
    if not comment_text:
        flash('Comment cannot be empty.', 'warning')
        return redirect(url_for('employee.ticket_detail', ticket_id=ticket.id))

    new_comment = TicketComment(
        ticket_id=ticket.id,
        user_id=session['user_id'],
        comment=comment_text
    )
    ticket.updated_at = datetime.now(timezone.utc)
    db.session.add(new_comment)
    db.session.commit()

    flash('Your update has been added to the ticket.', 'success')
    return redirect(url_for('employee.ticket_detail', ticket_id=ticket.id))
