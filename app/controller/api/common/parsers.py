from flask_restful import reqparse

def post_title(title):
	if len(title) > 128:
		raise ValueError("Title's length must have to be less than 128.")
	return title

def comment_body(body):
	if len(body) > 512:
		raise ValueError("Body's length must have to be less than 512.")
	return body

def user_name(name):
	if len(name) > 64:
		raise ValueError("name's length must have to be less than 64.")
	return name

def user_age(age):
	age =  int(age)
	if age > 200 or age < 0:
		raise ValueError("Age out of the range(0,200).")
	return age

def user_location(location):
	if len(location) > 128:
		raise ValueError("Location's length must have to be less than 128.")
	return location
	
page_parser = reqparse.RequestParser()
page_parser.add_argument("page", type=int, default=1, location="args")

post_aPost_parser = reqparse.RequestParser()
post_aPost_parser.add_argument('title', type=post_title, required=True, location="form")
post_aPost_parser.add_argument('body', type=str, required=True, location="form")

post_PostComments_parser = reqparse.RequestParser()
post_PostComments_parser.add_argument('body', type=comment_body, required=True, location="form")

post_aComment_parser = post_PostComments_parser.copy()

post_aUser_parser = reqparse.RequestParser()
post_aUser_parser.add_argument('name', type=user_name, location="form")
post_aUser_parser.add_argument('age', type=user_age, location="form")
post_aUser_parser.add_argument('location', type=user_location, location="form")
post_aUser_parser.add_argument("about_me", type=str, location="form")