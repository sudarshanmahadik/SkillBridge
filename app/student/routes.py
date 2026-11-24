from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import current_user, login_required
from app.extensions import db
from app.auth.routes import student_required
from app.models.user import User, StudentProfile
from app.models.career import CareerRole, RoleSkillRequirement
from app.models.skill import Skill, StudentSkill
from app.models.analysis import SkillGapAnalysis, SkillGapDetail
from app.models.roadmap import LearningRoadmap, RoadmapItem
from app.models.resource import LearningResource, StudentProgress
from app.services.skill_gap_service import calculate_skill_gap
from app.services.roadmap_service import generate_learning_roadmap, toggle_roadmap_item
from app.services.recommendation_service import get_recommended_resources_for_student

student_bp = Blueprint('student', __name__, url_prefix='/student')

LEVEL_SCORES = {
    'Beginner': 1,
    'Intermediate': 2,
    'Advanced': 3
}

@student_bp.route('/dashboard')
@login_required
@student_required
def dashboard():
    profile = current_user.profile
    target_role = profile.target_career_role if profile and profile.target_career_role else None

    # If no target role selected, pick default Python Developer or first available role
    if not target_role:
        target_role = CareerRole.query.filter_by(is_active=True).first()

    # Get latest gap analysis for target role
    latest_analysis = None
    if target_role:
        latest_analysis = SkillGapAnalysis.query.filter_by(
            user_id=current_user.id,
            career_role_id=target_role.id
        ).order_by(SkillGapAnalysis.created_at.desc()).first()

        # If not analyzed yet, run initial calculation
        if not latest_analysis:
            latest_analysis = calculate_skill_gap(current_user.id, target_role.id)

    # Get student's roadmap
    roadmap = None
    if target_role:
        roadmap = LearningRoadmap.query.filter_by(
            user_id=current_user.id,
            career_role_id=target_role.id
        ).first()
        if not roadmap and latest_analysis:
            roadmap = generate_learning_roadmap(current_user.id, latest_analysis.id)

    # Assessed skills count
    total_assessed_skills = StudentSkill.query.filter_by(user_id=current_user.id).count()

    # Recent activities (up to 5)
    recent_activities = StudentProgress.query.filter_by(
        user_id=current_user.id
    ).order_by(StudentProgress.timestamp.desc()).limit(5).all()

    # Recommended resources preview (up to 4)
    recommended_resources = get_recommended_resources_for_student(current_user.id, limit=4)

    return render_template(
        'student/dashboard.html',
        profile=profile,
        target_role=target_role,
        analysis=latest_analysis,
        roadmap=roadmap,
        total_assessed_skills=total_assessed_skills,
        recent_activities=recent_activities,
        recommended_resources=recommended_resources
    )


@student_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@student_required
def profile():
    user = current_user
    prof = user.profile
    if not prof:
        prof = StudentProfile(user_id=user.id)
        db.session.add(prof)
        db.session.commit()

    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'update_profile':
            user.full_name = request.form.get('full_name', user.full_name).strip()
            prof.phone = request.form.get('phone', prof.phone).strip()
            prof.institute = request.form.get('institute', prof.institute).strip()
            prof.degree = request.form.get('degree', prof.degree).strip()
            prof.semester = request.form.get('semester', prof.semester).strip()
            prof.github_url = request.form.get('github_url', prof.github_url).strip()
            prof.linkedin_url = request.form.get('linkedin_url', prof.linkedin_url).strip()
            prof.bio = request.form.get('bio', prof.bio).strip()

            target_role_id = request.form.get('target_career_role_id')
            if target_role_id and target_role_id.isdigit():
                prof.target_career_role_id = int(target_role_id)

            db.session.add(StudentProgress(
                user_id=user.id,
                activity_type='Profile Update',
                description='Updated personal and academic credentials'
            ))
            db.session.commit()
            flash('Profile details updated successfully.', 'success')
            return redirect(url_for('student.profile'))

        elif action == 'change_password':
            old_pass = request.form.get('old_password')
            new_pass = request.form.get('new_password')
            confirm_pass = request.form.get('confirm_password')

            if not user.check_password(old_pass):
                flash('Current password verification failed.', 'danger')
            elif len(new_pass) < 6:
                flash('New password must be at least 6 characters.', 'danger')
            elif new_pass != confirm_pass:
                flash('New passwords do not match.', 'danger')
            else:
                user.set_password(new_pass)
                db.session.commit()
                flash('Security password updated successfully.', 'success')
            return redirect(url_for('student.profile'))

    all_roles = CareerRole.query.filter_by(is_active=True).all()
    student_skills = StudentSkill.query.filter_by(user_id=user.id).all()

    return render_template(
        'student/profile.html',
        user=user,
        profile=prof,
        all_roles=all_roles,
        student_skills=student_skills
    )


@student_bp.route('/career-roles')
@login_required
@student_required
def career_roles():
    category = request.args.get('category', 'all').strip()
    search = request.args.get('search', '').strip()

    query = CareerRole.query.filter_by(is_active=True)

    if category and category != 'all':
        query = query.filter(CareerRole.category.ilike(f'%{category}%'))

    if search:
        query = query.filter(
            (CareerRole.title.ilike(f'%{search}%')) |
            (CareerRole.description.ilike(f'%{search}%'))
        )

    roles = query.all()
    categories = ['All', 'Web Development', 'Data & Analytics', 'Artificial Intelligence', 'Cloud & DevOps', 'Cybersecurity']
    
    # Get all role categories existing in DB
    db_cats = [r[0] for r in db.session.query(CareerRole.category).distinct().all() if r[0]]
    for c in db_cats:
        if c not in categories:
            categories.append(c)

    return render_template(
        'student/career_roles.html',
        roles=roles,
        categories=categories,
        active_category=category,
        search_query=search
    )


@student_bp.route('/select-career-role/<int:role_id>', methods=['POST'])
@login_required
@student_required
def select_career_role(role_id):
    role = CareerRole.query.get_or_404(role_id)
    profile = current_user.profile
    if not profile:
        profile = StudentProfile(user_id=current_user.id)
        db.session.add(profile)

    profile.target_career_role_id = role.id

    # Automatically recalculate skill gap analysis for this role
    analysis = calculate_skill_gap(current_user.id, role.id)
    # Generate/update roadmap
    generate_learning_roadmap(current_user.id, analysis.id)

    db.session.commit()
    flash(f'Target career set to {role.title}! Skill gap analysis calibrated.', 'success')
    return redirect(url_for('student.skill_gap_analysis'))


@student_bp.route('/skill-assessment', methods=['GET', 'POST'])
@login_required
@student_required
def skill_assessment():
    if request.method == 'POST':
        skill_id = request.form.get('skill_id')
        level = request.form.get('level')  # Beginner, Intermediate, Advanced, Remove

        if skill_id and level:
            skill = Skill.query.get(int(skill_id))
            if skill:
                existing = StudentSkill.query.filter_by(
                    user_id=current_user.id,
                    skill_id=skill.id
                ).first()

                if level == 'Remove':
                    if existing:
                        db.session.delete(existing)
                        db.session.commit()
                        flash(f'Removed {skill.name} from assessed skills.', 'info')
                else:
                    score = LEVEL_SCORES.get(level, 1)
                    if existing:
                        existing.proficiency_level = level
                        existing.proficiency_score = score
                    else:
                        new_ss = StudentSkill(
                            user_id=current_user.id,
                            skill_id=skill.id,
                            proficiency_level=level,
                            proficiency_score=score
                        )
                        db.session.add(new_ss)
                    db.session.commit()
                    flash(f'Updated {skill.name} to {level} level.', 'success')

        # Recalculate gap if student has target role
        if current_user.profile and current_user.profile.target_career_role_id:
            calculate_skill_gap(current_user.id, current_user.profile.target_career_role_id)

        return redirect(url_for('student.skill_assessment'))

    # Group skills by category
    all_skills = Skill.query.order_by(Skill.category, Skill.name).all()
    user_skills = StudentSkill.query.filter_by(user_id=current_user.id).all()
    user_skill_map = {us.skill_id: us.proficiency_level for us in user_skills}

    # Counts
    counts = {
        'total': len(user_skills),
        'beginner': sum(1 for us in user_skills if us.proficiency_level == 'Beginner'),
        'intermediate': sum(1 for us in user_skills if us.proficiency_level == 'Intermediate'),
        'advanced': sum(1 for us in user_skills if us.proficiency_level == 'Advanced')
    }

    # Group skills into category dictionary
    skills_by_cat = {}
    for s in all_skills:
        cat = s.category or 'General'
        skills_by_cat.setdefault(cat, []).append(s)

    target_role = current_user.profile.target_career_role if current_user.profile else None

    return render_template(
        'student/skill_assessment.html',
        skills_by_cat=skills_by_cat,
        user_skill_map=user_skill_map,
        counts=counts,
        target_role=target_role
    )


@student_bp.route('/skill-gap-analysis')
@login_required
@student_required
def skill_gap_analysis():
    profile = current_user.profile
    target_role = profile.target_career_role if profile and profile.target_career_role else None

    if not target_role:
        flash('Please select a target career role to view your skill gap analysis.', 'info')
        return redirect(url_for('student.career_roles'))

    # Calculate or fetch latest analysis
    analysis = calculate_skill_gap(current_user.id, target_role.id)
    details = SkillGapDetail.query.filter_by(analysis_id=analysis.id).all()

    # Prioritize into buckets
    skills_to_learn = [d for d in details if d.status == 'Missing Skill']
    skills_to_improve = [d for d in details if d.status == 'Improvement Needed']
    skills_available = [d for d in details if d.status == 'Skill Available']

    return render_template(
        'student/skill_gap_analysis.html',
        target_role=target_role,
        analysis=analysis,
        details=details,
        skills_to_learn=skills_to_learn,
        skills_to_improve=skills_to_improve,
        skills_available=skills_available
    )


@student_bp.route('/learning-roadmap')
@login_required
@student_required
def learning_roadmap():
    profile = current_user.profile
    target_role = profile.target_career_role if profile and profile.target_career_role else None

    if not target_role:
        flash('Please select a target career role first.', 'info')
        return redirect(url_for('student.career_roles'))

    roadmap = LearningRoadmap.query.filter_by(
        user_id=current_user.id,
        career_role_id=target_role.id
    ).first()

    if not roadmap:
        # Generate new roadmap
        analysis = calculate_skill_gap(current_user.id, target_role.id)
        roadmap = generate_learning_roadmap(current_user.id, analysis.id)

    # Group items by stage
    stages = {}
    for item in roadmap.items:
        stages.setdefault(item.stage_name, []).append(item)

    # Recommended resources map for skills in roadmap
    skill_resources = {}
    for item in roadmap.items:
        res = LearningResource.query.filter_by(skill_id=item.skill_id, is_active=True).limit(2).all()
        skill_resources[item.skill_id] = res

    return render_template(
        'student/learning_roadmap.html',
        target_role=target_role,
        roadmap=roadmap,
        stages=stages,
        skill_resources=skill_resources
    )


@student_bp.route('/roadmap/toggle-item/<int:item_id>', methods=['POST'])
@login_required
@student_required
def toggle_item(item_id):
    roadmap, is_completed = toggle_roadmap_item(current_user.id, item_id)
    if not roadmap:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'error': 'Item not found'}), 404
        flash('Milestone not found.', 'danger')
        return redirect(url_for('student.learning_roadmap'))

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'success': True,
            'is_completed': is_completed,
            'progress_percentage': roadmap.progress_percentage,
            'completed_items': roadmap.completed_items,
            'total_items': roadmap.total_items
        })

    status_str = "completed" if is_completed else "marked in-progress"
    flash(f'Milestone {status_str}!', 'success')
    return redirect(url_for('student.learning_roadmap'))


@student_bp.route('/resources')
@login_required
@student_required
def resources():
    res_type = request.args.get('type', 'all').strip()
    skill_filter = request.args.get('skill', 'all').strip()
    search = request.args.get('search', '').strip()

    query = LearningResource.query.filter_by(is_active=True)

    if res_type and res_type != 'all':
        query = query.filter_by(resource_type=res_type)

    if skill_filter and skill_filter != 'all' and skill_filter.isdigit():
        query = query.filter_by(skill_id=int(skill_filter))

    if search:
        query = query.filter(
            (LearningResource.title.ilike(f'%{search}%')) |
            (LearningResource.provider.ilike(f'%{search}%'))
        )

    all_resources = query.all()
    all_skills = Skill.query.order_by(Skill.name).all()
    resource_types = ['Documentation', 'Tutorial', 'Online Course', 'Video', 'Practice Website', 'Official Learning Platform']

    # Recommended resources specifically for this student
    recommended = get_recommended_resources_for_student(current_user.id, limit=6)

    return render_template(
        'student/resources.html',
        resources=all_resources,
        recommended=recommended,
        all_skills=all_skills,
        resource_types=resource_types,
        active_type=res_type,
        active_skill=skill_filter,
        search_query=search
    )
