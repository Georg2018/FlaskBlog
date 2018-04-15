'''
Auth blueprint's view. Defined the route of the auth blueprint and the related logic.
'''
import re
from flask import render_template, url_for, redirect
from flask_login import current_user, login_required, login_user, logout_user
from flask import flash
from .forms import RegisterForm, LoginForm
from . import auth
from .. import db
from .. import User

@auth.route('register', methods=['GET', 'POST'])
def register():
	form = RegisterForm()
	if form.validate_on_submit():
		user = User(email=form.email.data, username=form.username.data)
		user.set_password(form.password.data)

		db.session.add(user)
		db.session.commit()

		flash('You have successfully registered a account.')
		return redirect(url_for('auth.login'))

	return render_template('auth/register.html', form=form)

@auth.route('login', methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('main.index'))
	
	form = LoginForm()
	if form.validate_on_submit():
		if re.match('^[a-zA-Z0-9.]+@[a-zA-Z]+\.[a-zA-Z]+$', form.identifier.data):
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