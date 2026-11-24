import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'skillbridge-mca-mini-project-secret-key-2026')
    
    # Database Configuration: PostgreSQL with SQLite fallback
    pg_url = os.environ.get('DATABASE_URL')
    if pg_url and pg_url.startswith('postgres://'):
        # Fix for legacy postgres:// URI scheme
        pg_url = pg_url.replace('postgres://', 'postgresql://', 1)
        
    SQLALCHEMY_DATABASE_URI = pg_url or f"sqlite:///{os.path.join(basedir, 'skillbridge.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    } if 'postgresql' in (pg_url or '') else {}

    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(basedir, 'test_skillbridge.db')}"
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    DEBUG = False

config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
