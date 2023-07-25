from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField , TextAreaField , SelectField 
from wtforms.validators import DataRequired, Length, Email,EqualTo , ValidationError
from flaskproj import app 
from flaskproj.models import User
from flask_login import  current_user

class RegisterForm(FlaskForm):
    username = StringField('Username',
        validators=[DataRequired(),Length(min=2,max=20)])
    email = StringField('Email',
        validators=[DataRequired(),Email()])
    password = PasswordField('Password',
        validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
        validators=[DataRequired(),EqualTo('password')])
    submit = SubmitField('Sign Up')
    
    # custom validation for username
    def validate_username(self,username):
        with app.app_context():
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Username already exists')
            
    # custom validation for email
    def validate_email(self,email):
        with app.app_context():
            user = User.query.filter_by(email=email.data).first()
            if user :
                raise ValidationError('Email already exists')
    
    
    
class LoginForm(FlaskForm):
    username = StringField('Username',
        validators=[DataRequired(),Length(min=2,max=20)])
    password = PasswordField('Password',
        validators=[DataRequired()])
    submit = SubmitField('Login')                        
    

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=2, max=100)])
    content = TextAreaField('Content', validators=[DataRequired()])
    privacy = SelectField('Privacy', choices=[('public', 'Public'), ('friends only', 'Friends Only'), ('only me','Only Me')], validators=[DataRequired()])
    submit = SubmitField('Create Post')
    

class EditProfile(FlaskForm):
    username = StringField('Username',
        validators=[DataRequired(),Length(min=2,max=20)])
    email = StringField('Email',
        validators=[DataRequired(),Email()])
    old_password = PasswordField('Old Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), EqualTo('confirm_password', message='Passwords must match')])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired()])
    submit = SubmitField('Update')
    
    # custom validation for username
    def validate_username(self,username):
        with app.app_context():
            user = User.query.filter_by(username=username.data).first()
            
            if user and user.username != current_user.username:
                raise ValidationError('Username already exists')
            
    # custom validation for email
    def validate_email(self,email):
        with app.app_context():
            user = User.query.filter_by(email=email.data).first()
            if user and user.email != current_user.email:
                raise ValidationError('Email already exists')
            
class FriendRequestForm(FlaskForm):
   csrf_token = StringField(validators=[DataRequired()])
   submit = SubmitField('Send Request')
   

