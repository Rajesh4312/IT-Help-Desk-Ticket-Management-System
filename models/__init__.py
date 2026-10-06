from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .user import User
from .ticket import Ticket
from .comment import TicketComment

__all__ = ['db', 'User', 'Ticket', 'TicketComment']
