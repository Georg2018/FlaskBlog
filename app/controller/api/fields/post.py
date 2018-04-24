from flask_restful import fields
from .custom import Num, EdgeUrl, PaginateUrl

getPostField = {
    "id": fields.Integer,
    "author_name": fields.String(attribute="username"),
    "title": fields.String,
    "time": fields.DateTime(attribute="timestamp"),
    "comment_num": Num(attribute="comments"),
    "body": fields.String,
    "html": fields.String,
    "url": {"author": fields.Url("api.user", absolute=True), "comment": fields.String},
}

getPostsField = {
    "prev": EdgeUrl("api.posts", 0),
    "next": EdgeUrl("api.posts", 1),
    "all_pages": fields.Integer(attribute="pages"),
    "urls": fields.List(PaginateUrl("api.post", "postid", "id"), attribute="items"),
}

getFollowedPostsField = {
    "prev": EdgeUrl("api.followed_posts", 0),
    "next": EdgeUrl("api.followed_posts", 1),
    "all_pages": fields.Integer(attribute="pages"),
    "urls": fields.List(PaginateUrl("api.post", "postid", "id"), attribute="items"),
}

getPostCommentsField = {
    "prev": EdgeUrl("api.post_comments", 0),
    "next": EdgeUrl("api.post_comments", 1),
    "all_pages": fields.Integer(attribute="pages"),
    "urls": fields.List(
        PaginateUrl("api.comment", "commentid", "id"), attribute="items"
    ),
}
