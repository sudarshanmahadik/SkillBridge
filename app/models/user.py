from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app.extensions import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')  # 'student' or 'admin'
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    profile = db.relationship('StudentProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    skills = db.relationship('StudentSkill', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    analyses = db.relationship('SkillGapAnalysis', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    roadmaps = db.relationship('LearningRoadmap', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    progress_logs = db.relationship('StudentProgress', backref='user', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role == 'admin'

    def __repr__(self):
        return f'<User {self.email} ({self.role})>'


class StudentProfile(db.Model):
    __tablename__ = 'student_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    phone = db.Column(db.String(30), nullable=True)
    institute = db.Column(db.String(200), nullable=True)
    degree = db.Column(db.String(100), nullable=True)
    semester = db.Column(db.String(50), nullable=True)
    target_career_role_id = db.Column(db.Integer, db.ForeignKey('career_roles.id', ondelete='SET NULL'), nullable=True)
    github_url = db.Column(db.String(200), nullable=True)
    linkedin_url = db.Column(db.String(200), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to career role
    target_career_role = db.relationship('CareerRole', backref='interested_students')

    def __repr__(self):
        return f'<StudentProfile for User ID {self.user_id}>'
