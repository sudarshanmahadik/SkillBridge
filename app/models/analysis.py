from datetime import datetime
from app.extensions import db

class SkillGapAnalysis(db.Model):
    __tablename__ = 'skill_gap_analyses'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    career_role_id = db.Column(db.Integer, db.ForeignKey('career_roles.id', ondelete='CASCADE'), nullable=False)
    match_percentage = db.Column(db.Float, nullable=False, default=0.0)
    total_required_skills = db.Column(db.Integer, default=0)
    matched_skills_count = db.Column(db.Integer, default=0)
    upgrade_needed_count = db.Column(db.Integer, default=0)
    missing_skills_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    details = db.relationship('SkillGapDetail', backref='analysis', cascade='all, delete-orphan', lazy='joined')
    roadmap = db.relationship('LearningRoadmap', backref='analysis', uselist=False)

    def __repr__(self):
        return f'<SkillGapAnalysis ID={self.id} User={self.user_id} Role={self.career_role_id} Match={self.match_percentage}%>'


class SkillGapDetail(db.Model):
    __tablename__ = 'skill_gap_details'

    id = db.Column(db.Integer, primary_key=True)
    analysis_id = db.Column(db.Integer, db.ForeignKey('skill_gap_analyses.id', ondelete='CASCADE'), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id', ondelete='CASCADE'), nullable=False)
    student_level = db.Column(db.String(30), nullable=False)  # 'Not Available', 'Beginner', 'Intermediate', 'Advanced'
    required_level = db.Column(db.String(30), nullable=False)  # 'Beginner', 'Intermediate', 'Advanced'
    status = db.Column(db.String(40), nullable=False)  # 'Skill Available', 'Improvement Needed', 'Missing Skill'
    score_delta = db.Column(db.Integer, default=0)  # student_score - required_score

    # Relationship to Skill
    skill = db.relationship('Skill', lazy='joined')

    def __repr__(self):
        return f'<SkillGapDetail Analysis={self.analysis_id} Skill={self.skill_id} Status={self.status}>'
