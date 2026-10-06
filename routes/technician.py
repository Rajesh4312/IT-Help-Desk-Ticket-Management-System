from datetime import datetime, timezone
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, abort, current_app
from sqlalchemy import or_
from models import db, User, Ticket, TicketComment
from routes import technician_required

technician_bp = Blueprint('technician', __name__, url_prefix='/technician')


@technician_bp.route('/dashboard')
@technician_required
def dashboard():
    """Technician operations dashboard displaying queue metrics and active tickets."""
    total_tickets = Ticket.query.count()
    open_tickets = Ticket.query.filter_by(status='Open').count()
    in_progress_tickets = Ticket.query.filter_by(status='In Progress').count()
    resolved_tickets = Ticket.query.filter_by(status='Resolved').count()
    closed_tickets = Ticket.query.filter_by(status='Closed').count()

    # High / Critical tickets requiring urgent attention
    urgent_tickets_count = (
        Ticket.query.filter(
            Ticket.priority.in_(['High', 'Critical']),
            Ticket.status.in_(['Open', 'In Progress'])
        ).count()
    )

    # Unassigned queue count
    unassigned_count = Ticket.query.filter(
        Ticket.technician_id.is_(None),
        Ticket.status.in_(['Open', 'In Progress'])
    ).count()

    recent_tickets = (
        Ticket.query
        .order_by(Ticket.created_at.desc())
        .limit(10)
        .all()
    )

    metrics = {
        'total': total_tickets,
        'open': open_tickets,
        'in_progress': in_progress_tickets,
        'resolved': resolved_tickets,
        'closed': closed_tickets,
        'urgent': urgent_tickets_count,
        'unassigned': unassigned_count
    }

    return render_template(
        'technician/dashboard.html',
        metrics=metrics,
        recent_tickets=recent_tickets
    )


@technician_bp.route('/tickets')
@technician_required
def tickets():
    """Ticket management catalog with multi-field search and compound filters."""
    search_query = request.args.get('q', '').strip()
    status_filter = request.args.get('status', '').strip()
    priority_filter = request.args.get('priority', '').strip()
    category_filter = request.args.get('category', '').strip()

    query = Ticket.query.join(User, Ticket.employee_id == User.id)

    # Multi-term Search by ID, Employee name, or Problem Title
    if search_query:
        if search_query.isdigit():
            query = query.filter(
                or_(
                    Ticket.id == int(search_query),
                    Ticket.title.ilike(f'%{search_query}%'),
                    User.name.ilike(f'%{search_query}%'),
                    User.email.ilike(f'%{search_query}%')
                )
            )
        else:
            query = query.filter(
                or_(
                    Ticket.title.ilike(f'%{search_query}%'),
                    User.name.ilike(f'%{search_query}%'),
                    User.email.ilike(f'%{search_query}%'),
                    Ticket.description.ilike(f'%{search_query}%')
                )
            )

    # Compound Filters
    if status_filter and status_filter in current_app.config['STATUSES']:
        query = query.filter(Ticket.status == status_filter)

    if priority_filter and priority_filter in current_app.config['PRIORITIES']:
        query = query.filter(Ticket.priority == priority_filter)

    if category_filter and category_filter in current_app.config['CATEGORIES']:
        query = query.filter(Ticket.category == category_filter)

    # Order by urgency (Critical/High first, then created_at desc)
    all_tickets = query.order_by(Ticket.created_at.desc()).all()

    return render_template(
        'technician/tickets.html',
        tickets=all_tickets,
        search_query=search_query,
        selected_status=status_filter,
        selected_priority=priority_filter,
        selected_category=category_filter,
        categories=current_app.config['CATEGORIES'],
        priorities=current_app.config['PRIORITIES'],
        statuses=current_app.config['STATUSES']
    )


@technician_bp.route('/tickets/<int:ticket_id>')
@technician_required
def ticket_detail(ticket_id):
    """Technician ticket inspection, assignment, triage, and resolution workbench."""
    ticket = db.session.get(Ticket, ticket_id)
    if not ticket:
        abort(404)

    # Fetch all technicians for assignment dropdown
    technicians = User.query.filter_by(role='technician').order_by(User.name.asc()).all()

    return render_template(
        'technician/ticket_detail.html',
        ticket=ticket,
        technicians=technicians,
        categories=current_app.config['CATEGORIES'],
        priorities=current_app.config['PRIORITIES'],
        statuses=current_app.config['STATUSES']
    )


@technician_bp.route('/tickets/<int:ticket_id>/assign', methods=['POST'])
@technician_required
def assign_technician(ticket_id):
    """Assign or unassign an IT technician to a ticket."""
    ticket = db.session.get(Ticket, ticket_id)
    if not ticket:
        abort(404)

    technician_id_val = request.form.get('technician_id', '').strip()

    if not technician_id_val or technician_id_val == '0':
        ticket.technician_id = None
        action_desc = "unassigned"
    else:
        tech_user = db.session.get(User, int(technician_id_val))
        if not tech_user or tech_user.role != 'technician':
            flash('Invalid technician selected.', 'danger')
            return redirect(url_for('technician.ticket_detail', ticket_id=ticket.id))
        ticket.technician_id = tech_user.id
        action_desc = f"assigned to {tech_user.name}"
        # If still in Open, transition to In Progress upon assignment
        if ticket.status == 'Open':
            ticket.status = 'In Progress'

    ticket.updated_at = datetime.now(timezone.utc)

    # Record automatic audit comment in troubleshooting timeline
    current_tech = db.session.get(User, session['user_id'])
    audit_comment = TicketComment(
        ticket_id=ticket.id,
        user_id=session['user_id'],
        comment=f"[System Update] Ticket {action_desc} by {current_tech.name}."
    )
    db.session.add(audit_comment)
    db.session.commit()

    flash(f'Ticket #{ticket.id} successfully {action_desc}.', 'success')
    return redirect(url_for('technician.ticket_detail', ticket_id=ticket.id))


@technician_bp.route('/tickets/<int:ticket_id>/priority', methods=['POST'])
@technician_required
def change_priority(ticket_id):
    """Change priority level for a ticket."""
    ticket = db.session.get(Ticket, ticket_id)
    if not ticket:
        abort(404)

    new_priority = request.form.get('priority', '').strip()
    if new_priority not in current_app.config['PRIORITIES']:
        flash('Invalid priority level selected.', 'danger')
        return redirect(url_for('technician.ticket_detail', ticket_id=ticket.id))

    old_priority = ticket.priority
    ticket.priority = new_priority
    ticket.updated_at = datetime.now(timezone.utc)

    current_tech = db.session.get(User, session['user_id'])
    audit_comment = TicketComment(
        ticket_id=ticket.id,
        user_id=session['user_id'],
        comment=f"[Priority Changed] Priority updated from {old_priority} to {new_priority} by {current_tech.name}."
    )
    db.session.add(audit_comment)
    db.session.commit()

    flash(f'Priority updated to {new_priority}.', 'success')
    return redirect(url_for('technician.ticket_detail', ticket_id=ticket.id))


@technician_bp.route('/tickets/<int:ticket_id>/status', methods=['POST'])
@technician_required
def change_status(ticket_id):
    """Update ticket lifecycle status."""
    ticket = db.session.get(Ticket, ticket_id)
    if not ticket:
        abort(404)

    new_status = request.form.get('status', '').strip()
    if new_status not in current_app.config['STATUSES']:
        flash('Invalid status selected.', 'danger')
        return redirect(url_for('technician.ticket_detail', ticket_id=ticket.id))

    old_status = ticket.status
    ticket.status = new_status
    ticket.updated_at = datetime.now(timezone.utc)

    current_tech = db.session.get(User, session['user_id'])
    audit_comment = TicketComment(
        ticket_id=ticket.id,
        user_id=session['user_id'],
        comment=f"[Status Changed] Status transitioned from {old_status} to {new_status} by {current_tech.name}."
    )
    db.session.add(audit_comment)
    db.session.commit()

    flash(f'Ticket status updated to {new_status}.', 'success')
    return redirect(url_for('technician.ticket_detail', ticket_id=ticket.id))


@technician_bp.route('/tickets/<int:ticket_id>/comment', methods=['POST'])
@technician_required
def add_comment(ticket_id):
    """Add a technician troubleshooting note or internal investigation comment."""
    ticket = db.session.get(Ticket, ticket_id)
    if not ticket:
        abort(404)

    comment_text = request.form.get('comment', '').strip()
    if not comment_text:
        flash('Troubleshooting comment cannot be empty.', 'warning')
        return redirect(url_for('technician.ticket_detail', ticket_id=ticket.id))

    new_comment = TicketComment(
        ticket_id=ticket.id,
        user_id=session['user_id'],
        comment=comment_text
    )
    ticket.updated_at = datetime.now(timezone.utc)
    db.session.add(new_comment)
    db.session.commit()

    flash('Troubleshooting note added to ticket history.', 'success')
    return redirect(url_for('technician.ticket_detail', ticket_id=ticket.id))


@technician_bp.route('/tickets/<int:ticket_id>/resolve', methods=['POST'])
@technician_required
def resolve_ticket(ticket_id):
    """Record root cause resolution notes and advance ticket to Resolved or Closed."""
    ticket = db.session.get(Ticket, ticket_id)
    if not ticket:
        abort(404)

    resolution_notes = request.form.get('resolution_notes', '').strip()
    target_status = request.form.get('target_status', 'Resolved').strip()

    if not resolution_notes:
        flash('Resolution notes are required to resolve or close a ticket.', 'danger')
        return redirect(url_for('technician.ticket_detail', ticket_id=ticket.id))

    if target_status not in ['Resolved', 'Closed']:
        target_status = 'Resolved'

    ticket.resolution_notes = resolution_notes
    ticket.status = target_status
    ticket.updated_at = datetime.now(timezone.utc)

    current_tech = db.session.get(User, session['user_id'])
    audit_comment = TicketComment(
        ticket_id=ticket.id,
        user_id=session['user_id'],
        comment=f"[Resolution Added] {current_tech.name} marked ticket as {target_status}. Notes: {resolution_notes}"
    )
    db.session.add(audit_comment)
    db.session.commit()

    flash(f'Ticket #{ticket.id} marked as {target_status} with resolution notes.', 'success')
    return redirect(url_for('technician.ticket_detail', ticket_id=ticket.id))
