from datetime import datetime
from app.extensions import db

class Skill(db.Model):
    __tablename__ = 'skills'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(80), nullable=False, default='General')  # Programming, Backend, Frontend, Database, DevOps, etc.
    description = db.Column(db.Text, nullable=True)
    icon_name = db.Column(db.String(50), default='code')  # Material symbol name

    # Relationships
    resources = db.relationship('LearningResource', backref='skill', cascade='all, delete-orphan', lazy='dynamic')
    student_assessments = db.relationship('StudentSkill', backref='skill', cascade='all, delete-orphan', lazy='dynamic')

    def __repr__(self):
        return f'<Skill {self.code}: {self.name}>'


class StudentSkill(db.Model):
    __tablename__ = 'student_skills'
    __table_args__ = (
        db.UniqueConstraint('user_id', 'skill_id', name='uq_user_skill'),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id', ondelete='CASCADE'), nullable=False)
    proficiency_level = db.Column(db.String(30), nullable=False, default='Beginner')  # Beginner, Intermediate, Advanced
    proficiency_score = db.Column(db.Integer, nullable=False, default=1)  # 1, 2, 3
    assessed_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<StudentSkill User={self.user_id} Skill={self.skill_id} Level={self.proficiency_level}>'
