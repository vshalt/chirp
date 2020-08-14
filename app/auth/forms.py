from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, ValidationError
from wtforms.validators import DataRequired, Email, Length, EqualTo, Regexp
from app.models import User


class RegisterForm(FlaskForm):
    email               = StringField('Email', validators=[DataRequired(), Email(), Length(1, 64)])
    username            = StringField('Username', validators=[DataRequired(), Length(min=3, max=20), Regexp('^[a-zA-Z][a-zA-Z0-9_.]*$', flags=0, message='Can contain letters, numbers and _ .')])
    password            = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=20), EqualTo('confirm_password', message='Passwords must match')])
    confirm_password    = PasswordField('Confirm_password', validators=[DataRequired()])
    submit              = SubmitField('Sign Up')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('Email already exists')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already exists')


class LoginForm(FlaskForm):
    email       = StringField('Email', validators=[DataRequired(), Email(), Length(1, 64)])
    password    = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit      = SubmitField('Log In')


class UpdatePasswordForm(FlaskForm):
    old_password    = PasswordField('Old Password', validators=[DataRequired(), Length(min=8, max=20)])
    new_password    = PasswordField('New Password', validators=[DataRequired(), Length(min=8, max=20), EqualTo('new_password2', message='Passwords should match')])
    new_password2   = PasswordField('Confirm New Password', validators=[DataRequired()])
    submit          = SubmitField('Update Password')


class PasswordResetRequestForm(FlaskForm):
    email   = StringField('Email', validators=[DataRequired(), Email(), Length(1, 64)])
    submit  = SubmitField('Reset Password')


class PasswordResetForm(FlaskForm):
    password_1  = PasswordField('Enter Password', validators=[DataRequired(), Length(min=8, max=20), EqualTo('password_2', message='Passwords must match')])
    password_2  = PasswordField('Confirm Password', validators=[DataRequired()])
    submit      = SubmitField('Save Password')


class UpdateEmailForm(FlaskForm):
    email       = StringField('New Email', validators=[DataRequired(), Length(min=1, max=64), Email()])
    password    = PasswordField('Password', validators=[DataRequired()])
    submit      = SubmitField('Update Email')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already exists')


class UpdateUsernameForm(FlaskForm):
    username    = StringField('New Username', validators=[DataRequired(), Length(min=3, max=20), Regexp('^[a-zA-Z][a-zA_Z0-9_.]*$', flags=0, message='Can contain only alphabets,numbers and _ .')])
    password    = PasswordField('Password', validators=[DataRequired()])
    submit      = SubmitField('Update Username')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already exists')
