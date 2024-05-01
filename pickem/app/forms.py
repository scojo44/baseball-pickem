from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, URLField, HiddenField
from wtforms.validators import InputRequired, Optional, Length, URL

class UserAddForm(FlaskForm):
    """Form for adding users."""
    username = StringField('Username:', validators=[InputRequired()])
    password = PasswordField('Password:', validators=[Length(min=6)])
    confirm = PasswordField('Confirm:', validators=[Length(min=6)])

class UserProfileForm(UserAddForm):
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
