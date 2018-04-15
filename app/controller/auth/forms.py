from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Email, EqualTo, DataRequired, Length, Regexp, Optional
from wtforms import ValidationError
from .. import User

class RegisterForm(FlaskForm):
	email = StringField('Email', validators=[DataRequired(), Length(1,20), Email(), Regexp('^[a-zA-Z0-9.]+@[a-zA-Z0-9]+\.[a-zA-Z]+$', 0, 'Your email\'s format is invalid.')])
	username = StringField('Username', validators=[DataRequired(), Length(1,20), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, 'Username must have only letter, numbers, dots or underscores.')])
	password = PasswordField('Password', validators=[DataRequired(), Length(1,20), EqualTo("password2", message="The two password must match.")])
	password2 = PasswordField('Comfirm password.', validators=[DataRequired(), Length(1,20)])
	submit = SubmitField('Submit')

	def validate_email(self, field):
		if User.query.filter_by(email=field.data).first():
			raise ValidationError('This email has been used.')

	def validate_username(self, field):
		if User.query.filter_by(username=field.data).first():
			raise ValidationError('This uername has been used.')

class LoginForm(FlaskForm):
	identifier = StringField('Email or username', validators=[DataRequired(), Length(1,20)])
	password = PasswordField('Password', validators=[DataRequired(), Length(1,20)])
	remember_me = BooleanField('Remember me', validators=[Optional()])
	submit = SubmitField('Submit')
