from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from . import db


class User(db.Model):
    """User model representing employees and IT support technicians."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='employee')  # 'employee' or 'technician'
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def set_password(self, password):
        """Hash and store the user's password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify the user's password against the stored hash."""
        return check_password_hash(self.password_hash, password)

    def is_technician(self):
        """Check if user has technician privileges."""
        return self.role == 'technician'

    def is_employee(self):
        """Check if user has employee privileges."""
        return self.role == 'employee'

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"
