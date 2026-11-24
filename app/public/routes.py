from flask import Blueprint, render_template
from app.models.career import CareerRole
from app.models.skill import Skill
from app.models.user import User

public_bp = Blueprint('public', __name__)

@public_bp.route('/')
def index():
    featured_roles = CareerRole.query.filter_by(is_active=True).limit(6).all()
    stats = {
        'total_roles': CareerRole.query.count(),
        'total_skills': Skill.query.count(),
        'total_students': User.query.filter_by(role='student').count()
    }
    return render_template('public/landing.html', featured_roles=featured_roles, stats=stats)
