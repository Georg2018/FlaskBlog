from flask import Blueprint
from flask_restful import Api

api_bp = Blueprint('api', __name__, url_prefix='/api')
api = Api(api_bp)

from .common.auth import GetToken
api.add_resource(GetToken, '/token', endpoint='token')

from .resources.user import aUser, Users, Followers, Followings
api.add_resource(aUser, '/user/<string:username>', endpoint='user')
api.add_resource(Users, '/users', endpoint='users')
api.add_resource(Followers, '/user/<string:username>/followers', endpoint='followers')
api.add_resource(Followings, '/user/<string:username>/followings', endpoint='followings')

from .resources.post import aPost, Posts, FollowedPosts, PostComments
api.add_resource(aPost, '/post/<int:postid>', endpoint="post")
api.add_resource(Posts, '/posts', endpoint="posts")
api.add_resource(FollowedPosts, '/followedposts', endpoint="followd_posts")
api.add_resource(PostComments, '/post/<int:postid>/comments', endpoint="post_comments")

from .resources.comment import aComment
api.add_resource(aComment, '/comment/<int:commentid>', endpoint="comment")