from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Optional, URL
from app.models.user import User

class StudentLoginForm(FlaskForm):
    email = StringField('Academic Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember this session')
    submit = SubmitField('Sign In')


class StudentRegistrationForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('University / Personal Email', validators=[DataRequired(), Email(), Length(max=120)])
    institute = StringField('University / College Name', validators=[Optional(), Length(max=200)])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=6, message='Password must be at least 6 characters long.')
    ])
    confirm_password = PasswordField('Repeat Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match.')
    ])
    agree_terms = BooleanField('I agree to the Terms of Service & Privacy Policy', validators=[DataRequired(message='You must accept the terms.')])
    submit = SubmitField('Create Student Account')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.lower().strip()).first():
            raise ValidationError('An account with this email address already exists.')


class AdminLoginForm(FlaskForm):
    email = StringField('Admin Email', validators=[DataRequired(), Email()])
    password = PasswordField('Security Key / Password', validators=[DataRequired()])
    remember_me = BooleanField('Keep administrative session active')
    submit = SubmitField('Authenticate Admin')
