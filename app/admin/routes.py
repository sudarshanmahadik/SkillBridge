from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import current_user, login_required
from app.extensions import db
from app.auth.routes import admin_required
from app.models.user import User, StudentProfile
from app.models.career import CareerRole, RoleSkillRequirement
from app.models.skill import Skill, StudentSkill
from app.models.analysis import SkillGapAnalysis
from app.models.roadmap import LearningRoadmap
from app.models.resource import LearningResource, StudentProgress

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    stats = {
        'total_students': User.query.filter_by(role='student').count(),
        'total_roles': CareerRole.query.count(),
        'total_skills': Skill.query.count(),
        'total_resources': LearningResource.query.count(),
        'total_analyses': SkillGapAnalysis.query.count(),
        'total_roadmaps': LearningRoadmap.query.count(),
    }

    recent_students = User.query.filter_by(role='student').order_by(User.created_at.desc()).limit(8).all()
    recent_audits = StudentProgress.query.order_by(StudentProgress.timestamp.desc()).limit(10).all()

    return render_template(
        'admin/dashboard.html',
        stats=stats,
        recent_students=recent_students,
        recent_audits=recent_audits
    )


# ==========================================
# 1. STUDENT MANAGEMENT
# ==========================================
@admin_bp.route('/students', methods=['GET'])
@login_required
@admin_required
def manage_students():
    search = request.args.get('search', '').strip()
    status_filter = request.args.get('status', 'all').strip()

    query = User.query.filter_by(role='student')

    if search:
        query = query.filter(
            (User.full_name.ilike(f'%{search}%')) |
            (User.email.ilike(f'%{search}%'))
        )

    if status_filter == 'active':
        query = query.filter_by(is_active=True)
    elif status_filter == 'inactive':
        query = query.filter_by(is_active=False)

    students = query.order_by(User.created_at.desc()).all()
    return render_template('admin/manage_students.html', students=students, search_query=search, status_filter=status_filter)


@admin_bp.route('/students/toggle-status/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def toggle_student_status(user_id):
    student = User.query.get_or_404(user_id)
    if student.role != 'student':
        flash('Cannot change status of non-student accounts.', 'danger')
        return redirect(url_for('admin.manage_students'))

    student.is_active = not student.is_active
    db.session.commit()
    status_str = "activated" if student.is_active else "deactivated"
    flash(f"Student {student.full_name}'s account has been {status_str}.", 'success')
    return redirect(url_for('admin.manage_students'))


@admin_bp.route('/students/delete/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_student(user_id):
    student = User.query.get_or_404(user_id)
    if student.role != 'student':
        flash('Cannot delete non-student accounts here.', 'danger')
        return redirect(url_for('admin.manage_students'))

    name = student.full_name
    db.session.delete(student)
    db.session.commit()
    flash(f"Student {name} deleted successfully.", 'info')
    return redirect(url_for('admin.manage_students'))


# ==========================================
# 2. CAREER ROLE MANAGEMENT
# ==========================================
@admin_bp.route('/career-roles', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_career_roles():
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add':
            code = request.form.get('code', '').strip().upper()
            title = request.form.get('title', '').strip()
            category = request.form.get('category', '').strip()
            difficulty = request.form.get('difficulty_level', 'Intermediate').strip()
            salary = request.form.get('salary_range', '₹6 - ₹15 LPA').strip()
            demand = request.form.get('market_demand', 'High').strip()
            description = request.form.get('description', '').strip()

            if CareerRole.query.filter_by(code=code).first():
                flash(f'Role code {code} already exists.', 'danger')
            elif not title or not code:
                flash('Role title and code are required.', 'danger')
            else:
                role = CareerRole(
                    code=code,
                    title=title,
                    category=category,
                    difficulty_level=difficulty,
                    salary_range=salary,
                    market_demand=demand,
                    description=description,
                    is_active=True
                )
                db.session.add(role)
                db.session.commit()
                flash(f'Career Role "{title}" added successfully.', 'success')

        elif action == 'edit':
            role_id = request.form.get('role_id')
            role = CareerRole.query.get_or_404(int(role_id))
            role.title = request.form.get('title', role.title).strip()
            role.category = request.form.get('category', role.category).strip()
            role.difficulty_level = request.form.get('difficulty_level', role.difficulty_level).strip()
            role.salary_range = request.form.get('salary_range', role.salary_range).strip()
            role.market_demand = request.form.get('market_demand', role.market_demand).strip()
            role.description = request.form.get('description', role.description).strip()
            role.is_active = True if request.form.get('is_active') == 'on' else False
            db.session.commit()
            flash(f'Career Role "{role.title}" updated successfully.', 'success')

        elif action == 'delete':
            role_id = request.form.get('role_id')
            role = CareerRole.query.get_or_404(int(role_id))
            title = role.title
            db.session.delete(role)
            db.session.commit()
            flash(f'Career Role "{title}" deleted.', 'info')

        return redirect(url_for('admin.manage_career_roles'))

    roles = CareerRole.query.order_by(CareerRole.title).all()
    return render_template('admin/manage_career_roles.html', roles=roles)


# ==========================================
# 3. SKILL MANAGEMENT
# ==========================================
@admin_bp.route('/skills', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_skills():
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'add':
            code = request.form.get('code', '').strip().upper()
            name = request.form.get('name', '').strip()
            category = request.form.get('category', 'General').strip()
            icon_name = request.form.get('icon_name', 'code').strip()
            description = request.form.get('description', '').strip()

            if Skill.query.filter_by(code=code).first():
                flash(f'Skill code {code} already exists.', 'danger')
            elif not name or not code:
                flash('Skill name and unique code are required.', 'danger')
            else:
                skill = Skill(
                    code=code,
                    name=name,
                    category=category,
                    icon_name=icon_name,
                    description=description
                )
                db.session.add(skill)
                db.session.commit()
                flash(f'Skill "{name}" added successfully.', 'success')

        elif action == 'edit':
            skill_id = request.form.get('skill_id')
            skill = Skill.query.get_or_404(int(skill_id))
            skill.name = request.form.get('name', skill.name).strip()
            skill.category = request.form.get('category', skill.category).strip()
            skill.icon_name = request.form.get('icon_name', skill.icon_name).strip()
            skill.description = request.form.get('description', skill.description).strip()
            db.session.commit()
            flash(f'Skill "{skill.name}" updated successfully.', 'success')

        elif action == 'delete':
            skill_id = request.form.get('skill_id')
            skill = Skill.query.get_or_404(int(skill_id))
            name = skill.name
            db.session.delete(skill)
            db.session.commit()
            flash(f'Skill "{name}" deleted.', 'info')

        return redirect(url_for('admin.manage_skills'))

    skills = Skill.query.order_by(Skill.category, Skill.name).all()
    return render_template('admin/manage_skills.html', skills=skills)


# ==========================================
# 4. ROLE SKILL REQUIREMENTS MANAGEMENT
# ==========================================
@admin_bp.route('/role-requirements', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_role_requirements():
    selected_role_id = request.args.get('role_id', type=int)
    all_roles = CareerRole.query.order_by(CareerRole.title).all()
    all_skills = Skill.query.order_by(Skill.category, Skill.name).all()

    if not selected_role_id and all_roles:
        selected_role_id = all_roles[0].id

    selected_role = CareerRole.query.get(selected_role_id) if selected_role_id else None

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'add':
            career_role_id = int(request.form.get('career_role_id'))
            skill_id = int(request.form.get('skill_id'))
            req_level = request.form.get('required_level', 'Intermediate')
            importance = request.form.get('importance', 'Core')
            weight = int(request.form.get('weight', 3))

            score_map = {'Beginner': 1, 'Intermediate': 2, 'Advanced': 3}
            req_score = score_map.get(req_level, 2)

            existing = RoleSkillRequirement.query.filter_by(
                career_role_id=career_role_id,
                skill_id=skill_id
            ).first()

            if existing:
                existing.required_level = req_level
                existing.required_score = req_score
                existing.importance = importance
                existing.weight = weight
                flash('Requirement mapping updated.', 'success')
            else:
                new_req = RoleSkillRequirement(
                    career_role_id=career_role_id,
                    skill_id=skill_id,
                    required_level=req_level,
                    required_score=req_score,
                    importance=importance,
                    weight=weight
                )
                db.session.add(new_req)
                flash('Skill requirement mapped successfully.', 'success')

            db.session.commit()
            return redirect(url_for('admin.manage_role_requirements', role_id=career_role_id))

        elif action == 'delete':
            req_id = int(request.form.get('requirement_id'))
            req = RoleSkillRequirement.query.get_or_404(req_id)
            r_id = req.career_role_id
            db.session.delete(req)
            db.session.commit()
            flash('Requirement removed.', 'info')
            return redirect(url_for('admin.manage_role_requirements', role_id=r_id))

    requirements = []
    if selected_role:
        requirements = RoleSkillRequirement.query.filter_by(career_role_id=selected_role.id).all()

    return render_template(
        'admin/manage_role_requirements.html',
        all_roles=all_roles,
        selected_role=selected_role,
        all_skills=all_skills,
        requirements=requirements
    )


# ==========================================
# 5. LEARNING RESOURCES MANAGEMENT
# ==========================================
@admin_bp.route('/learning-resources', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_learning_resources():
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'add':
            skill_id = int(request.form.get('skill_id'))
            title = request.form.get('title', '').strip()
            provider = request.form.get('provider', '').strip()
            url = request.form.get('url', '').strip()
            res_type = request.form.get('resource_type', 'Documentation')
            difficulty = request.form.get('difficulty', 'Beginner')
            est_time = request.form.get('estimated_time', '3-5 Hours').strip()

            if not title or not url:
                flash('Title and URL are required.', 'danger')
            else:
                res = LearningResource(
                    skill_id=skill_id,
                    title=title,
                    provider=provider,
                    url=url,
                    resource_type=res_type,
                    difficulty=difficulty,
                    estimated_time=est_time,
                    is_active=True
                )
                db.session.add(res)
                db.session.commit()
                flash(f'Learning Resource "{title}" created successfully.', 'success')

        elif action == 'edit':
            res_id = int(request.form.get('resource_id'))
            res = LearningResource.query.get_or_404(res_id)
            res.skill_id = int(request.form.get('skill_id'))
            res.title = request.form.get('title', res.title).strip()
            res.provider = request.form.get('provider', res.provider).strip()
            res.url = request.form.get('url', res.url).strip()
            res.resource_type = request.form.get('resource_type', res.resource_type)
            res.difficulty = request.form.get('difficulty', res.difficulty)
            res.estimated_time = request.form.get('estimated_time', res.estimated_time).strip()
            res.is_active = True if request.form.get('is_active') == 'on' else False
            db.session.commit()
            flash(f'Learning Resource "{res.title}" updated.', 'success')

        elif action == 'delete':
            res_id = int(request.form.get('resource_id'))
            res = LearningResource.query.get_or_404(res_id)
            title = res.title
            db.session.delete(res)
            db.session.commit()
            flash(f'Resource "{title}" deleted.', 'info')

        return redirect(url_for('admin.manage_learning_resources'))

    resources = LearningResource.query.order_by(LearningResource.id.desc()).all()
    all_skills = Skill.query.order_by(Skill.name).all()
    resource_types = ['Documentation', 'Tutorial', 'Online Course', 'Video', 'Practice Website', 'Official Learning Platform']

    return render_template(
        'admin/manage_learning_resources.html',
        resources=resources,
        all_skills=all_skills,
        resource_types=resource_types
    )
