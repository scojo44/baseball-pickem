from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, URLField, HiddenField, RadioField
from wtforms.validators import InputRequired, Optional, Length, URL

class SignupForm(FlaskForm):
    """Form for adding users."""
    username = StringField('Username:', validators=[InputRequired()])
    password = PasswordField('Password:', validators=[Length(min=6)])
    confirm = PasswordField('Confirm:', validators=[Length(min=6)])

class UserProfileForm(SignupForm):
    """Form for editing the user profile."""
    header_image_url = URLField("(Optional) Header Image URL", validators=[Optional(), URL()])
    bio = TextAreaField("Your Bio", render_kw={"rows":6})
    location = StringField("Location")

class LoginForm(FlaskForm):
    """Login form."""
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])
    next = HiddenField()

class SecureEmptyForm(FlaskForm):
    """Form for secure fieldless forms.  WTForms will automatically add a hidden CRSF token."""

class GamePickForm(FlaskForm):
    """Form for picking the winner of a game."""
    picks = HiddenField('picks', validators=[InputRequired()])
