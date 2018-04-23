'''
The api's blueprint.
'''
from Flask import blueprint
from flask_restful import Api

api_bp = blueprint('api', __name__, url_prefix='api')
api = Api(api_blueprint)