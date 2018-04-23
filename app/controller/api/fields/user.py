from flask_restful import fields
from .custom import Num, EdgeUrl, PaginateUrl

getUserField = {
	"id": fields.Integer,
	"username": fields.String,
	"realname": fields.String(attribute="name"),
	"age": fields.Integer,
	"location": fields.String,
	"about_me": fields.String,
	"member_since": fields.DateTime,
	"last_since": fields.DateTime,
	"follower_num": Num(attribute="followers"),
	"following_num": Num(attribute="followings"),
	"article_num": Num(attribute="posts"),

	"urls": {
		"avatar_url": fields.String,
		"followers": fields.Url('api.followers', absolute=True),
		"followings": fields.Url('api.followings', absolute=True)
		}
}

getUsersField = {
	"prev_page": EdgeUrl('api.users', 0),
	"next_page": EdgeUrl('api.users', 1),
	"all_pages": fields.Integer(attribute="pages"),
	"users": fields.List(PaginateUrl('api.user', 'username', 'username'), attribute="items")
}

getFollowersField = {
	"prev_page": EdgeUrl('api.followers', 0),
	"next_page": EdgeUrl('api.followers', 1),
	"all_pages": fields.Integer(attribute="pages"),
	"followers": fields.List(PaginateUrl('api.user', 'username', 'username'), attribute="items")
}

getFollowingsField = {
	"prev_page": EdgeUrl('api.followings', 0),
	"next_page": EdgeUrl('api.followings', 1),
	"all_pages": fields.Integer(attribute="pages"),
	"followings": fields.List(PaginateUrl('api.user', 'username', 'username'), attribute="items")
}