from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Length, Email


class LoginForm(FlaskForm):
    name = StringField('name', validators=[InputRequired(message='Please enter a name'),Length(min=5)])
    password = PasswordField('pass', validators=[InputRequired(), Length(min=6, max=15)])


class SignupForm(FlaskForm):
    name = StringField('name', validators=[InputRequired(message='Please enter a name'),Length(min=5)])
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid Email'), Length(min=50)])
    model = StringField('model', validators=[InputRequired(message='Vehicle model required')])
    vid = StringField('vid', validators=[InputRequired(message='Vehicle License Number')])
    password = PasswordField('pass', validators=[InputRequired(message='Enter a password'), Length(min=6, max=15)])
