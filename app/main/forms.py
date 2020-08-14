from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, BooleanField, SelectField
from wtforms.validators import Length, Email, Regexp, ValidationError, DataRequired
from app.models import User, Role
from flask_pagedown.fields import PageDownField


class EditProfileForm(FlaskForm):
    name        = StringField('Name', validators=[Length(0, 64)])
    location    = StringField('Location', validators=[Length(0, 64)])
    about_me    = TextAreaField('About Me')
    submit      = SubmitField('Submit')


class EditProfileAdminForm(FlaskForm):
    name        = StringField('Name', validators=[Length(0, 64)])
    username    = StringField('Username', validators=[Length(0, 64), Regexp('^[a-zA-Z][a-zA-Z_.]*$', flags=0, message='Username must contain alphabets, numbers _.')])
    email       = StringField('Email', validators=[Email(), Length(0, 64)])
    role        = SelectField('Role', coerce=int)
    location    = StringField('Location', validators=[Length(0, 64)])
    about_me    = TextAreaField('About Me')
    confirmed   = BooleanField('Confirmed')
    submit      = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.user = user
        self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]

    def validate_email(self, field):
        if field.data != self.user.email and User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already exists')

    def validate_username(self, field):
        if field.data != self.user.username and User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already exists')


class PostForm(FlaskForm):
    body    = PageDownField('What\'s on your mind?', validators=[DataRequired()])
    submit  = SubmitField('Post')


class CommentForm(FlaskForm):
    body    = PageDownField('Post a reply.', validators=[DataRequired()])
    submit  = SubmitField('Reply')
