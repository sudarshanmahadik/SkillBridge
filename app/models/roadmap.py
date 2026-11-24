from datetime import datetime
from app.extensions import db

class LearningRoadmap(db.Model):
    __tablename__ = 'learning_roadmaps'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    career_role_id = db.Column(db.Integer, db.ForeignKey('career_roles.id', ondelete='CASCADE'), nullable=False)
    analysis_id = db.Column(db.Integer, db.ForeignKey('skill_gap_analyses.id', ondelete='CASCADE'), nullable=True)
    title = db.Column(db.String(150), nullable=False)
    progress_percentage = db.Column(db.Float, default=0.0)
    total_items = db.Column(db.Integer, default=0)
    completed_items = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    items = db.relationship('RoadmapItem', backref='roadmap', cascade='all, delete-orphan', order_by='RoadmapItem.sequence_order', lazy='joined')

    def recalculate_progress(self):
        if not self.items:
            self.progress_percentage = 0.0
            self.total_items = 0
            self.completed_items = 0
            return
        self.total_items = len(self.items)
        self.completed_items = sum(1 for item in self.items if item.is_completed)
        self.progress_percentage = round((self.completed_items / self.total_items) * 100.0, 1)

    def __repr__(self):
        return f'<LearningRoadmap ID={self.id} User={self.user_id} Progress={self.progress_percentage}%>'


class RoadmapItem(db.Model):
    __tablename__ = 'roadmap_items'

    id = db.Column(db.Integer, primary_key=True)
    roadmap_id = db.Column(db.Integer, db.ForeignKey('learning_roadmaps.id', ondelete='CASCADE'), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id', ondelete='CASCADE'), nullable=False)
    stage_name = db.Column(db.String(100), nullable=False)  # e.g. "Stage 1: Foundational Programming"
    sequence_order = db.Column(db.Integer, default=1, nullable=False)
    learning_objective = db.Column(db.Text, nullable=False)
    estimated_duration = db.Column(db.String(50), default='2 Weeks')
    is_completed = db.Column(db.Boolean, default=False, nullable=False)
    completed_at = db.Column(db.DateTime, nullable=True)

    # Relationship to Skill
    skill = db.relationship('Skill', lazy='joined')

    def __repr__(self):
        return f'<RoadmapItem Seq={self.sequence_order} Stage={self.stage_name} Completed={self.is_completed}>'
