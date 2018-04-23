from flask_restful import fields

apiToken = {
	"token": fields.String,
	"expiration": fields.Integer,
}