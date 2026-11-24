import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app import create_app
from app.extensions import db
from config import TestingConfig
from app.models.user import User, StudentProfile
from app.models.career import CareerRole, RoleSkillRequirement
from app.models.skill import Skill, StudentSkill
from app.models.analysis import SkillGapAnalysis, SkillGapDetail
from app.models.roadmap import LearningRoadmap, RoadmapItem
from app.models.resource import LearningResource, StudentProgress
from app.services.skill_gap_service import calculate_skill_gap
from app.services.roadmap_service import generate_learning_roadmap, toggle_roadmap_item

@pytest.fixture
def app():
    test_app = create_app(TestingConfig)
    with test_app.app_context():
        db.create_all()

        # Seed minimal data for testing
        admin = User(email='admin@test.edu', full_name='Test Admin', role='admin', is_active=True)
        admin.set_password('adminpass123')
        db.session.add(admin)

        student = User(email='student@test.edu', full_name='Test Student', role='student', is_active=True)
        student.set_password('studentpass123')
        db.session.add(student)
        db.session.flush()

        profile = StudentProfile(user_id=student.id, institute='Test University', degree='MCA')
        db.session.add(profile)

        role = CareerRole(
            code='CR-TEST',
            title='Python Test Developer',
            category='Backend',
            description='Test role description',
            difficulty_level='Intermediate',
            salary_range='₹6-12 LPA',
            market_demand='High'
        )
        db.session.add(role)

        skill1 = Skill(code='SK-P', name='Python', category='Programming')
        skill2 = Skill(code='SK-F', name='Flask', category='Backend')
        skill3 = Skill(code='SK-S', name='SQL', category='Database')
        db.session.add_all([skill1, skill2, skill3])
        db.session.flush()

        # Set requirements for role:
        # Python: Required Advanced (3), weight 5
        # Flask: Required Intermediate (2), weight 4
        # SQL: Required Intermediate (2), weight 3
        req1 = RoleSkillRequirement(career_role_id=role.id, skill_id=skill1.id, required_level='Advanced', required_score=3, weight=5)
        req2 = RoleSkillRequirement(career_role_id=role.id, skill_id=skill2.id, required_level='Intermediate', required_score=2, weight=4)
        req3 = RoleSkillRequirement(career_role_id=role.id, skill_id=skill3.id, required_level='Intermediate', required_score=2, weight=3)
        db.session.add_all([req1, req2, req3])

        # Resource for Python
        res = LearningResource(skill_id=skill1.id, title='Python Official', provider='Python.org', url='https://docs.python.org/3/', resource_type='Documentation')
        db.session.add(res)

        db.session.commit()

        yield test_app

        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()


# 1. PUBLIC LANDING PAGE
def test_landing_page(client):
    res = client.get('/')
    assert res.status_code == 200
    assert b'SkillBridge' in res.data
    assert b'Bridge Your Skills' in res.data


# 2. STUDENT AUTHENTICATION
def test_student_login_and_logout(client):
    # Login
    res = client.post('/auth/login', data={
        'email': 'student@test.edu',
        'password': 'studentpass123',
        'submit': 'Sign In'
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b'Welcome Back' in res.data or b'Student Console' in res.data or b'Dashboard' in res.data

    # Logout
    res_logout = client.get('/auth/logout', follow_redirects=True)
    assert res_logout.status_code == 200
    assert b'logged out' in res_logout.data.lower()


# 3. ADMIN AUTHENTICATION & ACCESS CONTROL
def test_admin_authentication_and_rbac(client):
    # Student cannot access admin login or admin dashboard
    client.post('/auth/login', data={'email': 'student@test.edu', 'password': 'studentpass123', 'submit': 'Sign In'})
    res_admin_dashboard = client.get('/admin/dashboard')
    assert res_admin_dashboard.status_code in (403, 302)

    client.get('/auth/logout')

    # Admin Login
    res = client.post('/auth/admin-login', data={
        'email': 'admin@test.edu',
        'password': 'adminpass123',
        'submit': 'Authenticate Admin'
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b'Admin Overview' in res.data or b'Admin Console' in res.data


# 4. STUDENT PROFILE UPDATE
def test_student_profile_update(client, app):
    client.post('/auth/login', data={'email': 'student@test.edu', 'password': 'studentpass123', 'submit': 'Sign In'})
    res = client.post('/student/profile', data={
        'action': 'update_profile',
        'full_name': 'Updated Student Name',
        'phone': '+91 99999 88888',
        'institute': 'National Institute of Tech',
        'degree': 'MCA',
        'semester': 'Sem 4',
        'github_url': 'github.com/test',
        'linkedin_url': 'linkedin.com/in/test',
        'bio': 'Passionate engineer'
    }, follow_redirects=True)
    assert res.status_code == 200

    with app.app_context():
        user = User.query.filter_by(email='student@test.edu').first()
        assert user.full_name == 'Updated Student Name'
        assert user.profile.institute == 'National Institute of Tech'


# 5. SKILL ASSESSMENT & PROFICIENCY STORAGE
def test_skill_assessment(client, app):
    client.post('/auth/login', data={'email': 'student@test.edu', 'password': 'studentpass123', 'submit': 'Sign In'})

    with app.app_context():
        skill1 = Skill.query.filter_by(code='SK-P').first()
        skill_id = skill1.id

    # Assess Python as Intermediate
    res = client.post('/student/skill-assessment', data={
        'skill_id': str(skill_id),
        'level': 'Intermediate'
    }, follow_redirects=True)
    assert res.status_code == 200

    with app.app_context():
        user = User.query.filter_by(email='student@test.edu').first()
        student_skill = StudentSkill.query.filter_by(user_id=user.id, skill_id=skill_id).first()
        assert student_skill is not None
        assert student_skill.proficiency_level == 'Intermediate'
        assert student_skill.proficiency_score == 2


# 6. SKILL GAP CALCULATION & MATHEMATICAL WEIGHTING
def test_skill_gap_calculation(app):
    with app.app_context():
        user = User.query.filter_by(email='student@test.edu').first()
        role = CareerRole.query.filter_by(code='CR-TEST').first()
        skill_p = Skill.query.filter_by(code='SK-P').first()
        skill_s = Skill.query.filter_by(code='SK-S').first()

        # Add assessed skills:
        # Python: Intermediate (2) [Required Advanced (3), weight 5] -> delta = -1, Improvement Needed
        # SQL: Beginner (1) [Required Intermediate (2), weight 3] -> delta = -1, Improvement Needed
        # Flask: Not assessed -> Missing Skill
        db.session.add(StudentSkill(user_id=user.id, skill_id=skill_p.id, proficiency_level='Intermediate', proficiency_score=2))
        db.session.add(StudentSkill(user_id=user.id, skill_id=skill_s.id, proficiency_level='Beginner', proficiency_score=1))
        db.session.commit()

        analysis = calculate_skill_gap(user.id, role.id)
        assert analysis is not None
        assert analysis.total_required_skills == 3
        assert analysis.matched_skills_count == 0
        assert analysis.upgrade_needed_count == 2
        assert analysis.missing_skills_count == 1

        # Check that match percentage is between 0 and 100
        assert 0.0 <= analysis.match_percentage <= 100.0

        # Details check
        details = SkillGapDetail.query.filter_by(analysis_id=analysis.id).all()
        assert len(details) == 3
        status_set = {d.status for d in details}
        assert 'Improvement Needed' in status_set
        assert 'Missing Skill' in status_set


# 7. LEARNING ROADMAP GENERATION & ITEM TOGGLE
def test_learning_roadmap_generation_and_toggle(app):
    with app.app_context():
        user = User.query.filter_by(email='student@test.edu').first()
        role = CareerRole.query.filter_by(code='CR-TEST').first()

        analysis = calculate_skill_gap(user.id, role.id)
        roadmap = generate_learning_roadmap(user.id, analysis.id)

        assert roadmap is not None
        assert len(roadmap.items) == 3
        first_item = roadmap.items[0]

        # Toggle completion
        toggled_roadmap, is_comp = toggle_roadmap_item(user.id, first_item.id)
        assert is_comp is True
        assert toggled_roadmap.progress_percentage > 0.0


# 8. ADMIN CRUD FOR CAREER ROLES
def test_admin_career_roles_crud(client, app):
    client.post('/auth/admin-login', data={'email': 'admin@test.edu', 'password': 'adminpass123', 'submit': 'Authenticate Admin'})

    # Create new role
    res_add = client.post('/admin/career-roles', data={
        'action': 'add',
        'code': 'CR-NEW',
        'title': 'DevOps Architect',
        'category': 'Cloud',
        'difficulty_level': 'Advanced',
        'salary_range': '₹12-20 LPA',
        'market_demand': 'Very High',
        'description': 'Automates deployment'
    }, follow_redirects=True)
    assert res_add.status_code == 200

    with app.app_context():
        role = CareerRole.query.filter_by(code='CR-NEW').first()
        assert role is not None
        assert role.title == 'DevOps Architect'
        role_id = role.id

    # Delete role
    res_del = client.post('/admin/career-roles', data={
        'action': 'delete',
        'role_id': str(role_id)
    }, follow_redirects=True)
    assert res_del.status_code == 200

    with app.app_context():
        assert CareerRole.query.filter_by(code='CR-NEW').first() is None


# 9. ADMIN CRUD FOR SKILLS, REQUIREMENTS, AND RESOURCES
def test_admin_skills_requirements_resources(client, app):
    client.post('/auth/admin-login', data={'email': 'admin@test.edu', 'password': 'adminpass123', 'submit': 'Authenticate Admin'})

    # 1. Add Skill
    res_skill = client.post('/admin/skills', data={
        'action': 'add',
        'code': 'SK-DOCKER',
        'name': 'Docker Containerization',
        'category': 'DevOps',
        'icon_name': 'inventory_2',
        'description': 'Containerization platform'
    }, follow_redirects=True)
    assert res_skill.status_code == 200

    with app.app_context():
        docker_skill = Skill.query.filter_by(code='SK-DOCKER').first()
        assert docker_skill is not None
        skill_id = docker_skill.id
        role = CareerRole.query.filter_by(code='CR-TEST').first()
        role_id = role.id

    # 2. Map Requirement to Role
    res_req = client.post('/admin/role-requirements', data={
        'action': 'add',
        'career_role_id': str(role_id),
        'skill_id': str(skill_id),
        'required_level': 'Intermediate',
        'importance': 'Core',
        'weight': '4'
    }, follow_redirects=True)
    assert res_req.status_code == 200

    with app.app_context():
        req = RoleSkillRequirement.query.filter_by(career_role_id=role_id, skill_id=skill_id).first()
        assert req is not None
        assert req.required_level == 'Intermediate'
        assert req.weight == 4

    # 3. Add Resource
    res_res = client.post('/admin/learning-resources', data={
        'action': 'add',
        'skill_id': str(skill_id),
        'title': 'Docker Docs Official',
        'provider': 'Docker',
        'url': 'https://docs.docker.com/',
        'resource_type': 'Documentation',
        'difficulty': 'Beginner',
        'estimated_time': '3 Hours'
    }, follow_redirects=True)
    assert res_res.status_code == 200

    with app.app_context():
        resource = LearningResource.query.filter_by(title='Docker Docs Official').first()
        assert resource is not None
        assert resource.url == 'https://docs.docker.com/'

