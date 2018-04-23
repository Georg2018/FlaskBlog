from flask_restful import reqparse

page_parser = reqparse.RequestParser()
page_parser.add_argument('page', type=int, default=1, location='args')