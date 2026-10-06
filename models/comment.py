from datetime import datetime, timezone
from . import db


class TicketComment(db.Model):
    """TicketComment model representing chronological updates, replies, and technician troubleshooting notes."""
    __tablename__ = 'ticket_comments'

    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    comment = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationship to user author
    user = db.relationship('User', backref=db.backref('comments', lazy='dynamic'))

    def __repr__(self):
        return f"<TicketComment #{self.id} on Ticket #{self.ticket_id}>"
