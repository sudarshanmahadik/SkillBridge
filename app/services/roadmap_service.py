from datetime import datetime
from app.extensions import db
from app.models.user import User
from app.models.career import CareerRole
from app.models.skill import Skill
from app.models.analysis import SkillGapAnalysis, SkillGapDetail
from app.models.roadmap import LearningRoadmap, RoadmapItem
from app.models.resource import StudentProgress

STAGE_CATEGORIES = {
    'Programming': 'Stage 1: Core Fundamentals & Programming Logic',
    'Frontend': 'Stage 2: Frontend Foundations & UI Components',
    'Backend': 'Stage 2: Backend Architecture & Server Engineering',
    'Database': 'Stage 2: Data Persistence & SQL Optimization',
    'Data Science': 'Stage 3: Data Analytics & Feature Engineering',
    'Machine Learning': 'Stage 3: Model Architecture & Evaluation',
    'DevOps': 'Stage 3: Containerization & Cloud Deployment',
    'Cloud': 'Stage 3: Cloud Infrastructure & Services',
    'Cybersecurity': 'Stage 3: Security Auditing & Threat Mitigation',
    'General': 'Stage 4: Practical Integration & Capstone Practice'
}

DEFAULT_DURATIONS = ['1-2 Weeks', '2 Weeks', '2-3 Weeks', '3 Weeks', '1 Week']

def generate_learning_roadmap(user_id, analysis_id=None):
    """
    Generates a personalized, structured multi-stage learning roadmap based on student's actual skill gaps.
    """
    user = User.query.get(user_id)
    if not user:
        return None

    # Get analysis
    if analysis_id:
        analysis = SkillGapAnalysis.query.get(analysis_id)
    else:
        analysis = SkillGapAnalysis.query.filter_by(user_id=user_id).order_by(SkillGapAnalysis.created_at.desc()).first()

    if not analysis:
        return None

    career_role = CareerRole.query.get(analysis.career_role_id)
    if not career_role:
        return None

    # Remove previous roadmap for this analysis if regenerating
    existing_roadmap = LearningRoadmap.query.filter_by(user_id=user_id, career_role_id=career_role.id).first()
    if existing_roadmap:
        db.session.delete(existing_roadmap)
        db.session.flush()

    roadmap = LearningRoadmap(
        user_id=user_id,
        career_role_id=career_role.id,
        analysis_id=analysis.id,
        title=f"{career_role.title} Accelerated Mastery Roadmap",
        progress_percentage=0.0,
        total_items=0,
        completed_items=0
    )
    db.session.add(roadmap)
    db.session.flush()

    # Prioritize gap details: Missing skills first, then Improvement Needed, then Available
    gap_details = SkillGapDetail.query.filter_by(analysis_id=analysis.id).all()
    
    # Sort: Missing skills first, then Improvement Needed
    priority_order = {'Missing Skill': 1, 'Improvement Needed': 2, 'Skill Available': 3}
    sorted_gaps = sorted(gap_details, key=lambda d: (priority_order.get(d.status, 4), d.skill.category))

    sequence = 1
    items_to_add = []

    for detail in sorted_gaps:
        skill = detail.skill
        cat = skill.category or 'General'
        stage_name = STAGE_CATEGORIES.get(cat, f"Stage {min(sequence, 4)}: Specialized Integration")

        if detail.status == 'Missing Skill':
            obj = f"Learn {skill.name} from ground up to achieve {detail.required_level} level competency required for {career_role.title}."
            dur = '2-3 Weeks'
            is_comp = False
        elif detail.status == 'Improvement Needed':
            obj = f"Upgrade existing {detail.student_level} skills in {skill.name} to target {detail.required_level} standard."
            dur = '1-2 Weeks'
            is_comp = False
        else:
            obj = f"Maintain and reinforce existing {detail.student_level} proficiency in {skill.name} through practical exercises."
            dur = '1 Week'
            is_comp = True  # Already meets or exceeds requirement!

        item = RoadmapItem(
            roadmap_id=roadmap.id,
            skill_id=skill.id,
            stage_name=stage_name,
            sequence_order=sequence,
            learning_objective=obj,
            estimated_duration=dur,
            is_completed=is_comp,
            completed_at=datetime.utcnow() if is_comp else None
        )
        items_to_add.append(item)
        sequence += 1

    db.session.add_all(items_to_add)
    db.session.flush()

    roadmap.recalculate_progress()

    progress = StudentProgress(
        user_id=user_id,
        activity_type='Roadmap Generated',
        description=f'Generated roadmap for {career_role.title} with {len(items_to_add)} learning milestones'
    )
    db.session.add(progress)
    db.session.commit()

    return roadmap


def toggle_roadmap_item(user_id, item_id):
    """
    Toggles completion status of a roadmap item and recalculates overall roadmap progress.
    """
    item = RoadmapItem.query.get(item_id)
    if not item or item.roadmap.user_id != user_id:
        return None, False

    item.is_completed = not item.is_completed
    item.completed_at = datetime.utcnow() if item.is_completed else None
    
    item.roadmap.recalculate_progress()

    status_str = "completed" if item.is_completed else "marked in-progress"
    progress = StudentProgress(
        user_id=user_id,
        activity_type='Milestone Progress',
        description=f'Milestone "{item.skill.name}" {status_str} in {item.roadmap.title}'
    )
    db.session.add(progress)
    db.session.commit()

    return item.roadmap, item.is_completed
