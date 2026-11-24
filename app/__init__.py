import os
from flask import Flask, render_template
from app.extensions import db, login_manager, csrf
from app.models.user import User

def create_app(config_class=None):
    app = Flask(__name__)
    
    if config_class is None:
        from config import DevelopmentConfig
        config_class = DevelopmentConfig
        
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    from app.public.routes import public_bp
    from app.auth.routes import auth_bp
    from app.student.routes import student_bp
    from app.admin.routes import admin_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(admin_bp)

    # Context Processors for templates
    @app.context_processor
    def inject_global_data():
        return {
            'app_name': 'SkillBridge',
            'current_year': 2026
        }

    # Custom Error Handlers
    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500

    return app
