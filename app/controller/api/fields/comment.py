from flask_restful import fields

getCommentField = {
	"id": fields.Integer,
	"time": fields.DateTime(attribute="timestamp"),
	"author_name": fields.String(attribute="username"),
	"article_id": fields.Integer(attribute="postid"),
	"body": fields.String,
	"urls": {
		"arthor": fields.Url("api.user", absolute=True),
		"post": fields.Url("api.post", absolute=True)
	}
}