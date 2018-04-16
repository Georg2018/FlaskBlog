'''
Auth blueprint's view. Defined the route of the auth blueprint and the related logic.
'''
import re
from flask import render_template, url_for, redirect, flash, request
from flask_login import current_user, login_required, login_user, logout_user
from .forms import RegisterForm, LoginForm
from . import auth
from .. import db
from .. import User, send_mail

@auth.before_app_request
def before_request():
	if current_user.is_authenticated:
		if not current_user.confirmed \
						and request.endpoint \
						and request.blueprint != 'auth' \
						and request.endpoint != 'static':
					return render_template('auth/unconfirmed.html')

@auth.route('register', methods=['GET', 'POST'])
def register():
	form = RegisterForm()
	if form.validate_on_submit():
		user = User(email=form.email.data, username=form.username.data, password=form.password.data)

		db.session.add(user)
		db.session.commit()

		token = user.generate_confirmed_token()

		send_mail(user.email, 'Confirmed your account.', '/auth/mail/confirmed', user=user, token=token)

		flash('You have successfully registered a account.')
		flash('We have send a confirmed email to your mailbox.Please check it for verification.')
		return redirect(url_for('auth.login'))

	return render_template('auth/register.html', form=form)

@auth.route('login', methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('main.index'))
	
	form = LoginForm()
	if form.validate_on_submit():
		if re.match('^[a-zA-Z0-9.]+@[a-zA-Z0-9]+\.[a-zA-Z]+$', form.identifier.data):
			user = User.query.filter_by(email=form.identifier.data).first()
		else:
			user = User.query.filter_by(username=form.identifier.data).first()

		if user is not None and user.check_password(form.password.data):
			login_user(user, form.remember_me.data)
			return redirect(url_for('main.index'))
		else:
			flash('Your username/email or password is invalid.')
			return redirect(url_for('auth.login'))

	return render_template('auth/login.html', form=form)

@auth.route('logout')
def logout():
	if not current_user.is_authenticated:
		flash('You have not logined in.')
		return redirect(url_for('main.index'))

	logout_user()
	return redirect(url_for('main.index'))

@auth.route('confirmed/<token>')
def confirmed(token):
	'''
	Email confirmed.
	'''
	if current_user.is_authenticated and current_user.confirmed:
		flash('You have been confirmed.')
		return redirect(url_for('main.index'))

	user_id = User.verify_confirmed_token(token)

	if user_id:
		flash('You have successfully verify your account.')
		return redirect(url_for('auth.login'))

	flash('Some errors are happend.')
	return redirect(url_for('main.index'))

@auth.route('resendMail')
def resendMail():
	'''
	Resend confirmed email.
	'''
	if current_user.confirmed:
		flash('You hace been confirmed.')
		return redirect(url_for('main.index'))

	if not current_user.is_authenticated:
		flash('You have not login.')
		return redirect(url_for('auth.login'))

	token = current_user.generate_confirmed_token()
	send_mail(current_user.email, 'Confirmed your account.', '/auth/mail/confirmed', user=current_user, token=token)

	flash('We have resent a confirmed email.')
	return render_template('auth/unconfirmed.html')
