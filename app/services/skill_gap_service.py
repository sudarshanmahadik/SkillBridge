from app.extensions import db
from app.models.user import User, StudentProfile
from app.models.career import CareerRole, RoleSkillRequirement
from app.models.skill import Skill, StudentSkill
from app.models.analysis import SkillGapAnalysis, SkillGapDetail
from app.models.resource import StudentProgress

LEVEL_SCORES = {
    'none': 0,
    'not available': 0,
    'beginner': 1,
    'intermediate': 2,
    'advanced': 3
}

def calculate_skill_gap(user_id, career_role_id):
    """
    Computes exact, mathematically weighted skill gap analysis for a student against a target career role.
    """
    user = User.query.get(user_id)
    role = CareerRole.query.get(career_role_id)
    if not user or not role:
        return None

    # Get all requirements for target role
    requirements = RoleSkillRequirement.query.filter_by(career_role_id=career_role_id).all()
    if not requirements:
        # No requirements defined yet
        analysis = SkillGapAnalysis(
            user_id=user_id,
            career_role_id=career_role_id,
            match_percentage=0.0,
            total_required_skills=0,
            matched_skills_count=0,
            upgrade_needed_count=0,
            missing_skills_count=0
        )
        db.session.add(analysis)
        db.session.commit()
        return analysis

    # Get all student's assessed skills as a dictionary: {skill_id: (level_str, score_int)}
    student_skills = StudentSkill.query.filter_by(user_id=user_id).all()
    student_skill_map = {ss.skill_id: (ss.proficiency_level, ss.proficiency_score) for ss in student_skills}

    total_weight = 0
    earned_weight = 0.0
    matched_count = 0
    upgrade_count = 0
    missing_count = 0

    gap_details_data = []

    for req in requirements:
        skill = req.skill
        req_score = req.required_score
        req_level = req.required_level
        weight = req.weight or 3
        total_weight += weight

        if req.skill_id in student_skill_map:
            stu_level, stu_score = student_skill_map[req.skill_id]
        else:
            stu_level, stu_score = ('Not Available', 0)

        delta = stu_score - req_score

        if stu_score == 0:
            status = 'Missing Skill'
            missing_count += 1
            ratio = 0.0
        elif stu_score < req_score:
            status = 'Improvement Needed'
            upgrade_count += 1
            ratio = min(1.0, stu_score / float(req_score))
        else:
            status = 'Skill Available'
            matched_count += 1
            ratio = 1.0

        earned_weight += weight * ratio

        gap_details_data.append({
            'skill_id': req.skill_id,
            'skill_name': skill.name,
            'category': skill.category,
            'student_level': stu_level,
            'student_score': stu_score,
            'required_level': req_level,
            'required_score': req_score,
            'status': status,
            'score_delta': delta,
            'importance': req.importance,
            'weight': weight
        })

    # Calculate match percentage
    match_percentage = round((earned_weight / total_weight) * 100.0, 1) if total_weight > 0 else 0.0

    # Save to database
    analysis = SkillGapAnalysis(
        user_id=user_id,
        career_role_id=career_role_id,
        match_percentage=match_percentage,
        total_required_skills=len(requirements),
        matched_skills_count=matched_count,
        upgrade_needed_count=upgrade_count,
        missing_skills_count=missing_count
    )
    db.session.add(analysis)
    db.session.flush()

    for item in gap_details_data:
        detail = SkillGapDetail(
            analysis_id=analysis.id,
            skill_id=item['skill_id'],
            student_level=item['student_level'],
            required_level=item['required_level'],
            status=item['status'],
            score_delta=item['score_delta']
        )
        db.session.add(detail)

    # Update student's target role in profile if not already set
    if user.profile and not user.profile.target_career_role_id:
        user.profile.target_career_role_id = career_role_id

    # Log progress activity
    progress = StudentProgress(
        user_id=user_id,
        activity_type='Gap Analysis',
        description=f'Completed skill gap analysis for {role.title} with {match_percentage}% readiness match'
    )
    db.session.add(progress)
    db.session.commit()

    return analysis
