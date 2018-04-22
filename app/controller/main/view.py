'''
The main blueprint's view. Defined the route of the main blueprint and the related logic.
'''
from flask import render_template, url_for, redirect, abort, flash, request, current_app, make_response
from flask_login import current_user, login_required
from flask_principal import Permission, UserNeed
from .forms import UserInfoForm, AdminInfoEditForm, PostForm, CommentForm
from . import main
from .. import User, Post, Comment, Follow, db, require, need, Permission as model_permission

@main.route('/')
def index():
	page = request.args.get('page', 1, type=int)
	show_followed = bool(request.cookies.get('show_followed', ''))

	if show_followed and current_user.is_authenticated:
		query = current_user.followed_posts
	else:
		query = Post.query.filter_by(disable=False).order_by(Post.timestamp.desc())

	pagination = query.paginate(page,\
								current_app.config.get('FLASK_POST_PER_PAGE', 20),\
								error_out=False)
	posts = pagination.items
	return render_template('main/index.html', posts=posts, pagination=pagination, show_followed=show_followed)

@main.route('/user/<username>')
def user(username):
	user = User.query.filter_by(username=username).first_or_404()
	page = request.args.get('page', 1, type=int)
	pagination = user.posts.filter_by(disable=False).order_by(Post.timestamp.desc()).paginate(page,
																current_app.config.get('FLASK_USERPOST_PER_PAGE', 20),
																error_out=False)
	posts = pagination.items
	return render_template('main/user.html', user=user, posts=posts, pagination=pagination)

@main.route('/editinfo', methods=['GET', 'POST'])
@require('editinfo')
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
@require('admin')
@login_required
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
@require('post')
@login_required
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
	post = Post.query.filter_by(disable=False, id=postid).first_or_404()
	page = request.args.get('page', 1, type=int)
	pagination = post.comments.filter_by(disable=False).order_by(Comment.timestamp.asc()).paginate(page,
																			current_app.config.get('FLASK_COMMENT_PER_PAGE', 20),
																			error_out=False)
	comments = pagination.items
	form = CommentForm()

	return render_template('/main/post.html', post=post, comments=comments, pagination=pagination, form=form)

@main.route('/postremove/<postid>')
@login_required
def post_remove(postid):
	'''Disable a post.'''

	post = Post.query.filter_by(disable=False, id=postid).first_or_404()

	if current_user.can('admin') or Permission(UserNeed(post.user.id)).can():
		post.disable = True
		db.session.add(post)
		db.session.commit()

		flash('The post "%s" has been removed'%(post.title))
		return redirect(url_for('main.index'))
	else:
		abort(403)

@main.route('/commentsubmit/<postid>', methods=['GET', 'POST'])
@require('comment')
@login_required
def comment_submit(postid):
	'''Submit a comment.'''
	post = Post.query.filter_by(disable=False, id=postid).first_or_404()

	form = CommentForm()
	if form.validate_on_submit():
		comment = Comment(body=form.body.data)
		comment.post = post
		comment.user = current_user._get_current_object()
		db.session.add(comment)
		db.session.commit()

		page = post.comments.count()//current_app.config.get('FLASK_COMMET_PER_PAGE', 20)+1
		flash('You have successfully add a comment.')
		return redirect(url_for('main.post', postid=post.id, page=page))

	return redirect(url_for('main.post', postid=post.id))

@main.route('/commentremove/<commentid>')
@login_required
def comment_remove(commentid):
	'''Remove a comment.'''
	comment = Comment.query.filter_by(disable=False, id=commentid).first_or_404()

	if current_user.can('admin') or Permission(UserNeed(comment.user.id)):
		comment.disable = True
		db.session.add(comment)
		db.session.commit()

		flash('You have successfully remove a comment.')
		return redirect(url_for('main.post', postid=comment.post.id))
	else:
		abort(403)

@main.route('/commentedit/<commentid>', methods=['GET', 'POST'])
@login_required
def comment_edit(commentid):
	'''Edit a comment.'''
	comment = Comment.query.get_or_404(commentid)

	if Permission(UserNeed(comment.user.id)) or current_user.can('admin'):
		form = CommentForm()

		if form.validate_on_submit():
			comment.body = form.body.data
			db.session.add(comment)
			db.session.commit()
			flash('You have successfully update a comment.')
			return redirect(url_for('main.post', postid=comment.post.id))

		form.body.data = comment.body
		return render_template('/main/editcomment.html', form=form, comment=comment)

@main.route('/follow/<userid>')
@login_required
@require('follow')
def follow(userid):
	if current_user.id == userid:
		flash("You can't follow yourself.")
		return redirect(url_for('main.index'))

	if not current_user.is_followed_user(userid):
		current_user.follow(userid)
		flash('You have successfully followed the user.')
		user = User.query.get(userid)
		return redirect(url_for('main.user', username=user.username))
	else:
		flash("You have followed the user.")
		return redirect('main.index')

@main.route('/unfollow/<userid>')
@login_required
@require('follow')
def unfollow(userid):
	if current_user.id == userid:
		flash("You can't unfollow yourself.")
		return redirect(url_for('main.index'))

	current_user.unfollow(userid)

	flash("You have successfully unfollow the user.")
	user = User.query.get(userid)
	return redirect(url_for('main.user', username=user.username))

@main.route('/user/<username>/followers')
@login_required
def followers(username):
	user = User.query.filter_by(username=username).first_or_404()
	page = request.args.get('page', 1, type=int)
	pagination = user.followers.order_by(Follow.timestamp.desc()).paginate(page,
																		current_app.config.get('FLASK_USER_PER_PAGE', 20),
																		error_out=False)
	followers = [item.follower for item in pagination.items]

	return render_template('/main/followers.html', users=followers, user=user, pagination=pagination)

@main.route('/user/<username>/followings')
@login_required
def followings(username):
	user = User.query.filter_by(username=username).first_or_404()
	page = request.args.get('page', 1, type=int)
	pagination = user.followings.order_by(Follow.timestamp.desc()).paginate(page,
																		current_app.config.get('FLASK_USER_PER_page', 20),
																		error_out=False)
	followings = [item.followed for item in pagination.items]

	return render_template('/main/followings.html', users=followings, user=user, pagination=pagination)

@main.route('/show_all')
def show_all():
	resp = make_response(redirect(url_for('main.index')))
	resp.set_cookie('show_followed', '', max_age=60*60*24*30)
	return resp

@main.route('/show_followed')
@login_required
def show_followed():
	resp = make_response(redirect(url_for('main.index')))
	resp.set_cookie('show_followed', '1', max_age=60*60*24*30)
	return resp