from flask import current_app, g
from flask_restful import Resource, marshal_with, abort
from ..common.parsers import page_parser
from ..common.auth import auth
from ..fields.post import getPostField, getPostsField, getFollowedPostsField, getPostCommentsField
from .. import User, Post as Post, Comment, Follow

class aPost(Resource):

	@marshal_with(getPostField)
	def get(self, postid):
		post = Post.query.filter_by(disable=False, id=postid).first()
		post.username = post.user.username
		return post

class Posts(Resource):
	@marshal_with(getPostsField)
	def get(self):
		page = page_parser.parse_args()['page']
		pagination = Post.query.filter_by(disable=False).order_by(Post.timestamp.desc())\
								.paginate(page, current_app.config.get('FLASK_PER_POST_PAGE', 20),\
								error_out=False)
		return pagination

class FollowedPosts(Resource):
	method_decorators = [auth.login_required]

	@marshal_with(getFollowedPostsField)
	def get(self):
		page = page_parser.parse_args()['page']
		pagination = g.current_user.followed_posts.paginate(page, \
															current_app.config.get('FLASK_PER_POST_PAGE', 20),\
															error_out=False)
		return pagination

class PostComments(Resource):
	@marshal_with(getPostCommentsField)
	def get(self, postid):
		page = page_parser.parse_args()['page']
		post = Post.query.filter_by(disable=False, id=postid).first()
		if not post:
			abort(404, message='Post not found')
		pagination = post.comments.order_by(Comment.timestamp.desc())\
								  .paginate(page, current_app.config.get('FLASK_COMMENT_PER_PAGE', 20),\
								   error_out=False)
		return pagination