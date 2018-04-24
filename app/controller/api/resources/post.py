from flask import current_app, g
from flask_restful import Resource, marshal_with, abort
from ..common.parsers import page_parser, post_aPost_parser
from ..common.auth import auth, can
from ..fields.post import (
    getPostField, getPostsField, getFollowedPostsField
)
from .. import User, Post as Post, Comment, Follow, db


class aPost(Resource):
    method_decorators = {
        "put": [can('post'), auth.login_required],
        "post": [can('post'), auth.login_required]
    }

    @marshal_with(getPostField)
    def get(self, postid=""):
        post = Post.query.filter_by(disable=False, id=postid).first()
        if not post:
            abort(404, message="Post not found.")
        post.username = post.user.username
        post.postid = post.id
        return post

    @marshal_with(getPostField)
    def put(self):
        form = post_aPost_parser.parse_args()
        post = Post(title=form['title'], body=form['body'])
        post.user = g.current_user
        db.session.add(post)
        db.session.commit()
        post.username = post.user.username
        post.postid = post.id
        return post

    @marshal_with(getPostField)
    def post(self, postid=""):
        post = Post.query.filter_by(disable=False, id=postid).first()
        if not post:
            abort(404, messgae="Post not found.")
        form = post_aPost_parser.parse_args()
        post.title = form["title"]
        post.body = form["body"]
        db.session.add(post)
        db.session.commit()
        post.username = post.user.username
        post.postid = post.id
        return post


class Posts(Resource):

    @marshal_with(getPostsField)
    def get(self):
        page = page_parser.parse_args()["page"]
        pagination = Post.query.filter_by(disable=False).order_by(
            Post.timestamp.desc()
        ).paginate(
            page, current_app.config.get("FLASK_PER_POST_PAGE", 20), error_out=False
        )
        return pagination


class FollowedPosts(Resource):
    method_decorators = [auth.login_required]

    @marshal_with(getFollowedPostsField)
    def get(self):
        page = page_parser.parse_args()["page"]
        pagination = g.current_user.followed_posts.paginate(
            page, current_app.config.get("FLASK_PER_POST_PAGE", 20), error_out=False
        )
        return pagination


class UserPosts(Resource):

    @marshal_with(getPostsField)
    def get(self, username):
        user = User.query.filter_by(username=username).first()
        if not user:
            abort(404, message="User not found.")
        page = page_parser.parse_args()["page"]
        pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
            page,
            current_app.config.get('FLASK_PER_POST_PAGE', 20),
            error_out=False)
        return pagination