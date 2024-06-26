"""Form definitions for WTForms."""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, URLField, HiddenField, RadioField
from wtforms.validators import InputRequired, Optional, Length, URL, EqualTo

PASSWORD_LENGTH = 6

class SignupForm(FlaskForm):
    """Form for adding users."""
    username = StringField('Username:', validators=[InputRequired()])
    password = PasswordField('Password:', validators=[Length(min=PASSWORD_LENGTH)])
    confirm = PasswordField('Confirm Password:', validators=[InputRequired(), EqualTo('password', 'Passwords did not match')])
    image_url = URLField("(Optional) Image URL:", validators=[Optional(), URL()])

class UserProfileForm(FlaskForm):
    """Form for editing the user profile."""
    username = StringField('Username:', validators=[InputRequired()])
    image_url = URLField("(Optional) Image URL:", validators=[Optional(), URL()])
    password = PasswordField('To confirm your changes, enter your password:', validators=[Length(min=6)])
    # bio = TextAreaField("Your Bio", render_kw={"rows":6})
    # location = StringField("Location")

class LoginForm(FlaskForm):
    """Login form."""
    username = StringField('Username:', validators=[InputRequired()])
    password = PasswordField('Password:', validators=[Length(min=PASSWORD_LENGTH)])
    next = HiddenField()

class ChangePasswordForm(FlaskForm):
    """Change password form."""
    password = PasswordField('Current Password:', validators=[Length(min=PASSWORD_LENGTH)])
    new_password = PasswordField('New Password:', validators=[Length(min=PASSWORD_LENGTH)])
    confirm = PasswordField('Confirm Password:', validators=[InputRequired(), EqualTo('new_password', 'Passwords did not match')])

class GamePickForm(FlaskForm):
    """Form for picking the winnerd of games."""
    picks = HiddenField('picks', validators=[InputRequired()]) # Will hold a json array of picks

class SecureEmptyForm(FlaskForm):
    """Form for secure fieldless forms.  WTForms will automatically add a hidden CRSF token."""
