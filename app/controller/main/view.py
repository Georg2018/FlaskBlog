'''
The main blueprint's view. Defined the route of the main blueprint and the related logic.
'''
from flask import render_template, url_for, redirect, abort, flash, request, current_app
from flask_login import current_user, login_required
from flask_principal import Permission
from .forms import UserInfoForm, AdminInfoEditForm
from . import main
from .. import User, db, require, need, Permission as model_permission

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

@main.route('/adminedit/<username>', methods=['GET', 'POST'])
@require('admin')
def admin_info_edit(username):
	user = User.query.filter_by(username=username).first_or_404()
	
	form = AdminInfoEditForm()
	form.user = user
	form.permission.choices = [(permission.name, permission.name) for permission in model_permission.query.order_by(model_permission.id.asc()).all()]
	if form.validate_on_submit():
		user.email = form.email.data
		user.confirmed = form.confirmed.data
		user.username = form.username.data
		user.active = form.active.data

		user.name = form.name.data
		user.age = form.age.data
		user.location = form.location.data
		user.about_me = form.about_me.data

		user.permissions = []
		for new_permission in form.permission.data:
			new_permission = model_permission.query.filter_by(name=new_permission).first()
			user.permissions.append(new_permission)

		try:
			db.session.add(user)
			db.session.commit()
			flash('Updata successfully.')
			return redirect(url_for('main.user', username=user.username))
		except:
			db.session.rollback()
			flash('Failture.')

	form.email.data = user.email
	form.confirmed.data = user.confirmed
	form.username.data = user.username
	form.active.data = user.active
	form.name.data = user.name
	form.age.data = user.age
	form.location.data = user.location
	form.about_me.data = user.about_me

	user_permissions = ''.join([permission.name for permission in user.permissions.all()])
	return render_template('main/adminedit.html', form=form, user_permission=user_permissions, user=user)

@main.route('/authsetting')
def account_setting():
	if current_user.is_anonymous:
		return redirect(url_for('main.index'))

	return render_template('main/account_setting.html')


@main.route('/users/')
def users():
	page = request.args.get('page', 1, type=int)
	pagination = User.query.order_by(User.member_since.desc()).paginate(page, per_page=current_app.config.get('FLASK_USER_PER_PAGE', 20), error_out=False)
	users = pagination.items
	return render_template('/main/users.html', users=users, pagination=pagination)
