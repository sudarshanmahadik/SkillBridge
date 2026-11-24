from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_user, logout_user, current_user, login_required
from app.extensions import db
from app.models.user import User, StudentProfile
from app.models.resource import StudentProgress
from app.auth.forms import StudentLoginForm, StudentRegistrationForm, AdminLoginForm

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in with administrator credentials.', 'warning')
            return redirect(url_for('auth.admin_login', next=request.url))
        if not current_user.is_admin:
            flash('Access Restricted: Administrator privileges required.', 'danger')
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def student_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access your student portal.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        if current_user.is_admin:
            flash('Redirected to Admin Dashboard.', 'info')
            return redirect(url_for('admin.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('student.dashboard'))

    login_form = StudentLoginForm()
    register_form = StudentRegistrationForm()
    active_tab = request.args.get('tab', 'login')

    if login_form.submit.data and login_form.validate_on_submit():
        email = login_form.email.data.lower().strip()
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(login_form.password.data):
            if not user.is_active:
                flash('Your account has been deactivated. Please contact administrator.', 'danger')
                return render_template('auth/login_register.html', login_form=login_form, register_form=register_form, active_tab='login')

            login_user(user, remember=login_form.remember_me.data)
            flash(f'Welcome back, {user.full_name}!', 'success')
            next_page = request.args.get('next')
            if user.is_admin:
                return redirect(next_page or url_for('admin.dashboard'))
            return redirect(next_page or url_for('student.dashboard'))
        else:
            flash('Invalid email address or password. Please try again.', 'danger')
            active_tab = 'login'

    return render_template('auth/login_register.html', login_form=login_form, register_form=register_form, active_tab=active_tab)

@auth_bp.route('/register', methods=['POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('student.dashboard'))

    login_form = StudentLoginForm()
    register_form = StudentRegistrationForm()

    if register_form.validate_on_submit():
        email = register_form.email.data.lower().strip()
        full_name = register_form.full_name.data.strip()
        institute = register_form.institute.data.strip() if register_form.institute.data else None

        # Create new student user
        user = User(
            email=email,
            full_name=full_name,
            role='student',
            is_active=True
        )
        user.set_password(register_form.password.data)
        db.session.add(user)
        db.session.flush()

        # Create corresponding profile
        profile = StudentProfile(
            user_id=user.id,
            institute=institute,
            degree='MCA / Computer Science'
        )
        db.session.add(profile)

        # Log progress event
        log = StudentProgress(
            user_id=user.id,
            activity_type='Registration',
            description='Created student account on SkillBridge'
        )
        db.session.add(log)
        db.session.commit()

        login_user(user)
        flash('Account created successfully! Welcome to SkillBridge.', 'success')
        return redirect(url_for('student.profile'))
    else:
        # Errors in registration
        for field, errors in register_form.errors.items():
            for error in errors:
                flash(f"{error}", 'danger')
        return render_template('auth/login_register.html', login_form=login_form, register_form=register_form, active_tab='register')

@auth_bp.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated and current_user.is_admin:
        return redirect(url_for('admin.dashboard'))

    form = AdminLoginForm()
    if form.validate_on_submit():
        email = form.email.data.lower().strip()
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(form.password.data):
            if not user.is_admin:
                flash('Access Denied: This portal requires administrator privileges.', 'danger')
                return render_template('auth/admin_login.html', form=form)

            login_user(user, remember=form.remember_me.data)
            flash('Administrative authentication verified.', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('admin.dashboard'))
        else:
            flash('Invalid administrator credentials.', 'danger')

    return render_template('auth/admin_login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been safely logged out.', 'info')
    return redirect(url_for('public.index'))
