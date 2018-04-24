from flask import current_app, g
from flask_restful import Resource, marshal_with, abort
from ..common.parsers import page_parser, post_aComment_parser, post_PostComments_parser
from ..common.auth import auth, can
from ..fields.comment import getCommentField, getPostCommentsField
from .. import User, Post, Follow, Comment, db


class aComment(Resource):
    method_decorators = {"post": [can("comment"), auth.login_required]}

    @marshal_with(getCommentField)
    def get(self, commentid):
        comment = Comment.query.filter_by(disable=False, id=commentid).first()
        if not comment:
            abort(404, message="Comment not found.")
        comment.username = comment.user.username
        comment.postid = comment.post.id
        return comment

    @marshal_with(getCommentField)
    def post(self, commentid):
        comment = Comment.query.filter_by(disable=False, id=commentid).first()
        if not comment:
            abort(404, message="Comment not found.")
        form = post_aComment_parser.parse_args()
        comment.body = form.body
        db.session.add(comment)
        db.session.commit()
        comment.username = comment.user.username
        comment.postid = comment.post.id
        return comment


class PostComments(Resource):
    method_decorators = {"put": [can("comment"), auth.login_required]}

    @marshal_with(getPostCommentsField)
    def get(self, postid):
        page = page_parser.parse_args()["page"]
        post = Post.query.filter_by(disable=False, id=postid).first()
        if not post:
            abort(404, message="Post not found")
        pagination = post.comments.order_by(Comment.timestamp.desc()).paginate(
            page, current_app.config.get("FLASK_COMMENT_PER_PAGE", 20), error_out=False
        )
        return pagination

    @marshal_with(getCommentField)
    def put(slef, postid):
        post = Post.query.filter_by(disable=False, id=postid).first()
        if not post:
            abort(404, message="Post not found.")
        form = post_PostComments_parser.parse_args()
        comment = Comment(body=form["body"], post=post, user=g.current_user)
        db.session.add(comment)
        db.session.commit()
        comment.username = g.current_user.username
        comment.postid = post.id
        return comment
