from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Email, EqualTo, DataRequired, Length, Regexp, Optional
from wtforms import ValidationError
from .. import User

class RegisterForm(FlaskForm):
	email = StringField('Email', validators=[DataRequired(), Length(1,20), Email()])
	username = StringField('Username', validators=[DataRequired(), Length(1,20), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, 'Username must have only letter, numbers, dots or underscores.')])
	password = PasswordField('Password', validators=[DataRequired(), Length(8,20), EqualTo("password2", message="The two password must matched.")])
	password2 = PasswordField('Comfirm password.', validators=[DataRequired()])
	submit = SubmitField('Submit')

	def validate_email(self, field):
		if User.query.filter_by(email=field.data).first():
			raise ValidationError('This email has been used.')

	def validate_username(self, field):
		if User.query.filter_by(username=field.data).first():
			raise ValidationError('This uername has been used.')

class LoginForm(FlaskForm):
	identifier = StringField('Email or username', validators=[DataRequired(), Length(1,20)])
	password = PasswordField('Password', validators=[DataRequired()])
	remember_me = BooleanField('Remember me', validators=[Optional()])
	submit = SubmitField('Submit')

class ChangePasswordForm(FlaskForm):
	old_password = PasswordField('Password', validators=[DataRequired()])
	new_password = PasswordField('New password', validators=[DataRequired(), Length(8,20), EqualTo('new_password2', message="Two new password must matched.")])
	new_password2 = PasswordField('Confirmed new password', validators=[DataRequired()])
	submit = SubmitField('Submit')

class ChangeMailForm(FlaskForm):
	password = PasswordField('Password', validators=[DataRequired()])
	new_email = StringField('New email', validators=[DataRequired(), Length(1,20), Email()])
	submit = SubmitField('Submit')

	def validate_new_email(slef, field):
		if User.query.filter_by(email=field.data).first():
			raise ValidationError('This email has been used.')

class AuthResetPassForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	submit = SubmitField('Submit')

class ResetPassForm(FlaskForm):
	password = PasswordField('Password', validators=[DataRequired()])
	submit = SubmitField('Submit')