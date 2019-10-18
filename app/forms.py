from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, \
    IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, \
    Regexp
from app.models import User, Quote

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember me')
    submit = SubmitField('Get Online!')

class SignupForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Regexp(
        '^[a-zA-Z0-9_]+$', message="Letters, numbers, and underscores only please.")])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Verify Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Get on the Net!')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('This username is already in use.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('This email is already in use.')

class SubmitForm(FlaskForm):
    body = StringField('Body', validators=[DataRequired()])
    speaker = StringField('Speaker', validators=[DataRequired()])
    topic = StringField('On', validators=[DataRequired()])
    submit = SubmitField('Submit quote')

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Verify Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset password')

class DenyQuoteForm(FlaskForm):
    id = IntegerField('Quote ID', validators=[DataRequired()])
    reason = StringField('Reason', validators=[DataRequired()])
    submit = SubmitField('Submit')
