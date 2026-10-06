import os
from datetime import datetime, timezone
from flask import Flask, render_template, session
from config import config_by_name, DevelopmentConfig
from models import db, User


def create_app(config_name=None):
    """Application factory for the IT Help Desk Ticket Management System."""
    app = Flask(__name__)

    # Load configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app.config.from_object(config_by_name.get(config_name, DevelopmentConfig))

    # Ensure instance folder exists for SQLite storage
    os.makedirs(app.config.get('INSTANCE_DIR', os.path.join(app.root_path, 'instance')), exist_ok=True)

    # Initialize extensions
    db.init_app(app)

    # Register Blueprints
    from routes.auth import auth_bp
    from routes.employee import employee_bp
    from routes.technician import technician_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(employee_bp)
    app.register_blueprint(technician_bp)

    # Global template context processor
    @app.context_processor
    def inject_context():
        current_user = None
        if 'user_id' in session:
            current_user = db.session.get(User, session['user_id'])
        return {
            'current_user': current_user,
            'current_year': datetime.now(timezone.utc).year
        }

    # Custom Error Handlers
    @app.errorhandler(400)
    def bad_request_error(error):
        return render_template('errors/400.html', error=error), 400

    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html', error=error), 403

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html', error=error), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html', error=error), 500

    # Initialize database tables
    with app.app_context():
        db.create_all()

    return app


if __name__ == '__main__':
    application = create_app()
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting IT Help Desk Ticket Management System on http://127.0.0.1:{port}")
    application.run(host='127.0.0.1', port=port, debug=True)
