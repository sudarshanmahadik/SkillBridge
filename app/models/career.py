from datetime import datetime
from app.extensions import db

class CareerRole(db.Model):
    __tablename__ = 'career_roles'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    title = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(80), nullable=False, default='General IT')
    description = db.Column(db.Text, nullable=False)
    difficulty_level = db.Column(db.String(30), default='Intermediate')  # Beginner, Intermediate, Advanced
    salary_range = db.Column(db.String(60), default='₹6 - ₹15 LPA')
    market_demand = db.Column(db.String(30), default='High')  # High, Very High, Growing
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    requirements = db.relationship('RoleSkillRequirement', backref='career_role', cascade='all, delete-orphan', lazy='joined')
    analyses = db.relationship('SkillGapAnalysis', backref='career_role', lazy='dynamic')
    roadmaps = db.relationship('LearningRoadmap', backref='career_role', lazy='dynamic')

    @property
    def total_required_skills(self):
        return len(self.requirements)

    def __repr__(self):
        return f'<CareerRole {self.code}: {self.title}>'


class RoleSkillRequirement(db.Model):
    __tablename__ = 'role_skill_requirements'
    __table_args__ = (
        db.UniqueConstraint('career_role_id', 'skill_id', name='uq_role_skill'),
    )

    id = db.Column(db.Integer, primary_key=True)
    career_role_id = db.Column(db.Integer, db.ForeignKey('career_roles.id', ondelete='CASCADE'), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id', ondelete='CASCADE'), nullable=False)
    required_level = db.Column(db.String(30), nullable=False, default='Intermediate')  # Beginner, Intermediate, Advanced
    required_score = db.Column(db.Integer, nullable=False, default=2)  # 1, 2, 3
    importance = db.Column(db.String(30), default='Core')  # Core, Recommended, Optional
    weight = db.Column(db.Integer, default=3)  # 1 to 5 scale

    # Relationships
    skill = db.relationship('Skill', backref='role_mappings', lazy='joined')

    def __repr__(self):
        return f'<RoleSkillRequirement Role={self.career_role_id} Skill={self.skill_id} Level={self.required_level}>'
