'''
The main blueprint's view. Defined the route of the main blueprint and the related logic.
'''
from flask import render_template, url_for, redirect, abort, flash, request, current_app
from flask_login import current_user, login_required
from flask_principal import Permission, UserNeed
from .forms import UserInfoForm, AdminInfoEditForm, PostForm
from . import main
from .. import User, Post, db, require, need, Permission as model_permission

@main.route('/')
def index():
	page = request.args.get('page', 1, type=int)
	pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page,
																current_app.config.get('FLASK_POST_PER_PAGE', 20),
																error_out=False)
	posts = pagination.items
	return render_template('main/index.html', posts=posts, pagination=pagination)

@main.route('/user/<username>')
def user(username):
	user = User.query.filter_by(username=username).first_or_404()
	page = request.args.get('page', 1, type=int)
	pagination = user.posts.order_by(Post.timestamp.desc()).paginate(page,
																current_app.config.get('FLASK_USERPOST_PER_PAGE', 20),
																error_out=False)
	posts = pagination.items
	return render_template('main/user.html', user=user, posts=posts, pagination=pagination)

@main.route('/editinfo', methods=['GET', 'POST'])
@login_required
def user_info_edit():
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
@login_required
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

@main.route('/authsetting/')
@login_required
def account_setting():
	return render_template('main/account_setting.html')


@main.route('/users/')
def users():
	'''Show all of the users' breif introduction.'''
	page = request.args.get('page', 1, type=int)
	pagination = User.query.order_by(User.member_since.desc()).paginate(page, per_page=current_app.config.get('FLASK_USER_PER_PAGE', 20), error_out=False)
	users = pagination.items
	return render_template('/main/users.html', users=users, pagination=pagination)

@main.route('/postsubmit', methods=['GET', 'POST'])
@login_required
@require('post')
def post_submit():
	'''Submit a new post.'''
	form = PostForm()
	if form.validate_on_submit():
		user = current_user._get_current_object()
		post = Post(title=form.title.data, body=form.body.data, user=user)
		db.session.add(user)
		db.session.add(post)
		db.session.commit()

		flash('You have successfully submited a article.')
		return redirect(url_for('main.post', postid=post.id))

	return render_template('/main/editpost.html', form=form, postid=None)

@main.route('/postedit/<postid>', methods=['GET', 'POST'])
@login_required
@require('post')
def post_edit(postid):
	'''Edit a exits article.'''
	post = Post.query.get_or_404(postid)
	if Permission(UserNeed(post.user.id)).can() or current_user.can('admin'):
		form = PostForm()
		if form.validate_on_submit():
			post.title = form.title.data
			post.body = form.body.data
			db.session.add(post)
			db.session.commit()

			flash('You have successfully updated a article.')
			return redirect(url_for('main.post', postid=post.id))

		form.title.data = post.title
		form.body.data = post.body
		return render_template('/main/editpost.html', form=form, postid=post.id)
	else:
		abort(403)

@main.route('/post/<postid>')
def post(postid):
	'''Show a post.'''
	post = Post.query.get_or_404(postid)

	return render_template('/main/post.html', post=post)