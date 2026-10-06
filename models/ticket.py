from datetime import datetime, timezone
from . import db


class Ticket(db.Model):
    """Ticket model tracking IT support issues and their full lifecycle."""
    __tablename__ = 'tickets'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    priority = db.Column(db.String(20), nullable=False, default='Medium')
    status = db.Column(db.String(20), nullable=False, default='Open')
    
    # Foreign Keys
    employee_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    technician_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime, 
        default=lambda: datetime.now(timezone.utc), 
        onupdate=lambda: datetime.now(timezone.utc)
    )
    resolution_notes = db.Column(db.Text, nullable=True)

    # Relationships
    employee = db.relationship(
        'User', 
        foreign_keys=[employee_id], 
        backref=db.backref('created_tickets', lazy='dynamic')
    )
    technician = db.relationship(
        'User', 
        foreign_keys=[technician_id], 
        backref=db.backref('assigned_tickets', lazy='dynamic')
    )
    comments = db.relationship(
        'TicketComment', 
        backref='ticket', 
        cascade='all, delete-orphan', 
        order_by='TicketComment.created_at.asc()'
    )

    @property
    def status_badge_class(self):
        """Map ticket status to Bootstrap badge styling."""
        mapping = {
            'Open': 'bg-primary',
            'In Progress': 'bg-warning text-dark',
            'Resolved': 'bg-success',
            'Closed': 'bg-secondary'
        }
        return mapping.get(self.status, 'bg-light text-dark')

    @property
    def priority_badge_class(self):
        """Map ticket priority to Bootstrap badge styling."""
        mapping = {
            'Low': 'bg-info text-dark',
            'Medium': 'bg-secondary',
            'High': 'bg-warning text-dark',
            'Critical': 'bg-danger'
        }
        return mapping.get(self.priority, 'bg-light text-dark')

    def __repr__(self):
        return f"<Ticket #{self.id}: {self.title[:30]} ({self.status})>"
