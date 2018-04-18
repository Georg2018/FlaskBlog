'''
The main blueprint's view. Defined the route of the main blueprint and the related logic.
'''
from flask import render_template, url_for, redirect, abort, flash, request
from flask_login import current_user, login_required
from .forms import UserInfoForm
from . import main
from .. import User, db

@main.route('/')
def index():
	return render_template('main/index.html')

@main.route('/user/<username>')
def user(username):
	user = User.query.filter_by(username=username).first_or_404()

	return render_template('main/user.html', user=user)

@main.route('/editinfo', methods=['GET', 'POST'])
def user_info_edit():
	if current_user.is_anonymous:
		return redirect(url_for('main.index'))

	form = UserInfoForm()
	if form.validate_on_submit():
		user = current_user._get_current_object()
		user.name = form.name.data
		user.age = form.age.data
		user.location = form.location.data
		user.about_me = form.about_me.data

		db.session.add(user)
		db.session.commit()

		flash('You have successfully updated your profile.')
		return redirect(url_for('main.user', username=user.username))

	form.name.data = current_user.name
	form.age.data = current_user.age
	form.location.data = current_user.location
	form.about_me.data = current_user.about_me

	return render_template('main/editinfo.html', form=form)

@main.route('/authsetting')
def account_setting():
	if current_user.is_anonymous:
		return redirect(url_for('main.index'))

	return render_template('main/account_setting.html')
