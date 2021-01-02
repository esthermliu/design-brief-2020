from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from app.models import User

class LoginForm(FlaskForm): # Have to pass FLaskForm in as the default
    username = StringField("Username", validators=[DataRequired()]) # render_kw={"placeholder": "test"}
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm): 
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Teacher or Student?', choices=[(0, 'Teacher'),(1,'Student')], coerce=int)
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()]) # Username input field
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)]) # TextAreaField is a multi-line box where the user can enter text, has to be between 0 and 140 characters, 140 matches space in database (check models)
    submit = SubmitField('Submit') 