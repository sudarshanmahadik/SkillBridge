from app.models.resource import LearningResource
from app.models.analysis import SkillGapAnalysis, SkillGapDetail
from app.models.skill import Skill

def get_recommended_resources_for_student(user_id, limit=12):
    """
    Retrieves curated learning resources prioritized for skills where the student has an active skill gap.
    """
    latest_analysis = SkillGapAnalysis.query.filter_by(user_id=user_id).order_by(SkillGapAnalysis.created_at.desc()).first()
    
    if not latest_analysis:
        # Fallback to general active resources
        return LearningResource.query.filter_by(is_active=True).limit(limit).all()

    # Get skill IDs needing improvement or missing
    gap_details = SkillGapDetail.query.filter_by(analysis_id=latest_analysis.id).all()
    priority_skill_ids = [d.skill_id for d in gap_details if d.status in ('Missing Skill', 'Improvement Needed')]

    if not priority_skill_ids:
        # If student met all skills, return resources for all role skills
        priority_skill_ids = [d.skill_id for d in gap_details]

    resources = LearningResource.query.filter(
        LearningResource.skill_id.in_(priority_skill_ids),
        LearningResource.is_active == True
    ).limit(limit).all()

    # If few resources found, supplement with other popular active resources
    if len(resources) < limit:
        existing_ids = [r.id for r in resources]
        supplements = LearningResource.query.filter(
            LearningResource.is_active == True,
            ~LearningResource.id.in_(existing_ids)
        ).limit(limit - len(resources)).all()
        resources.extend(supplements)

    return resources

def get_resources_by_skill(skill_id):
    """Returns all learning resources mapped to a specific skill."""
    return LearningResource.query.filter_by(skill_id=skill_id, is_active=True).all()
