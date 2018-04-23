'''
Add the support for HTTPBasicAuth to api blueprint.
'''
from flask_httpauth import HTTPBasicAuth
from . import api
from .. import User

