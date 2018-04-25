from flask_restful import fields
from .custom import Num, EdgeUrl, PaginateUrl

getCommentField = {
    "id": fields.Integer,
    "time": fields.DateTime(attribute="timestamp"),
    "author_name": fields.String(attribute="username"),
    "article_id": fields.Integer(attribute="postid"),
    "body": fields.String,
    "urls": {
        "arthor": fields.Url("api.user", absolute=True),
        "post": fields.Url("api.post", absolute=True),
    },
}

getPostCommentsField = {
    "prev": EdgeUrl("api.post_comments", 0),
    "next": EdgeUrl("api.post_comments", 1),
    "all_comments": fields.Integer(attribute="total"),
    "all_pages": fields.Integer(attribute="pages"),
    "urls": fields.List(
        PaginateUrl("api.comment", "commentid", "id"), attribute="items"
    ),
}
