from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextField, SubmitField
from wtforms.validators import Length, NumberRange
from wtforms import ValidationError
from .. import User

class UserInfoForm(FlaskForm):
	name = StringField('Name', validators=[Length(1,32)])
	age = IntegerField('Age', validators=[NumberRange(1,200, "You must input a valid number.")])
	location = StringField('Location', validators=[Length(1,64)])
	about_me = TextField('About me', validators=[Length(1,1000)])
	submit = SubmitField('Submit')