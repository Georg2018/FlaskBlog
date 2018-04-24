from flask import current_app, g
from flask_restful import Resource, marshal_with, abort
from ..common.parsers import page_parser
from ..common.auth import auth
from ..fields.comment import getCommentField
from .. import User, Post, Follow, Comment


class aComment(Resource):

    @marshal_with(getCommentField)
    def get(self, commentid):
        comment = Comment.query.filter_by(disable=False).first()
        if not comment:
            abort(404, message="Comment not found")
        comment.username = comment.user.username
        comment.postid = comment.post.id
        return comment
