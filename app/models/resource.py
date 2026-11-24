from datetime import datetime
from app.extensions import db

class LearningResource(db.Model):
    __tablename__ = 'learning_resources'

    id = db.Column(db.Integer, primary_key=True)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    resource_type = db.Column(db.String(50), nullable=False, default='Documentation')  # Documentation, Tutorial, Course, Video, Practice
    provider = db.Column(db.String(100), nullable=False, default='Official')
    url = db.Column(db.String(300), nullable=False)
    estimated_time = db.Column(db.String(50), default='3-5 Hours')
    difficulty = db.Column(db.String(30), default='Beginner')  # Beginner, Intermediate, Advanced
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    def __repr__(self):
        return f'<LearningResource {self.title} ({self.resource_type})>'


class StudentProgress(db.Model):
    __tablename__ = 'student_progress'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    activity_type = db.Column(db.String(50), nullable=False)  # 'Assessment', 'Gap Analysis', 'Roadmap', 'Profile Update'
    description = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f'<StudentProgress User={self.user_id} Activity={self.activity_type} Time={self.timestamp}>'
