import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    """Base configuration settings."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'helpdesk-secret-key-dev-2026-secure')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Instance folder database path
    INSTANCE_DIR = os.path.join(basedir, 'instance')
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', 
        f"sqlite:///{os.path.join(INSTANCE_DIR, 'helpdesk.db')}"
    )

    # Allowed Domain Constants
    CATEGORIES = [
        'Hardware',
        'Software',
        'Network',
        'Email',
        'Printer',
        'Account/Login',
        'Other'
    ]

    PRIORITIES = [
        'Low',
        'Medium',
        'High',
        'Critical'
    ]

    STATUSES = [
        'Open',
        'In Progress',
        'Resolved',
        'Closed'
    ]


class DevelopmentConfig(Config):
    """Development environment configuration."""
    DEBUG = True


class TestingConfig(Config):
    """Testing environment configuration."""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """Production environment configuration."""
    DEBUG = False
    # Ensure SECRET_KEY is set in environment for real deployments
    SECRET_KEY = os.environ.get('SECRET_KEY', 'replace-this-with-strong-prod-secret-key')


config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
