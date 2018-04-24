"""
Add the support for HTTPBasicAuth to api blueprint.
"""
from flask_httpauth import HTTPBasicAuth
from flask_restful import Resource, abort, marshal_with
from flask import g
from functools import wraps
from ..fields.auth import apiToken
from ..app import api
from .. import User

auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(username_or_token, password):
    if bool(password) == False:
        token = username_or_token
        g.current_user = User.verify_api_token(token)
        if g.current_user:
            g.token = token
            return True

        else:
            return False

    else:
        username = username_or_token
        user = User.query.filter_by(username=username).first()
        if user.check_password(password):
            g.current_user = user
            return True

        else:
            return False


class GetToken(Resource):
    method_decorators = [auth.login_required]

    @marshal_with(apiToken)
    def get(self):
        if g.get("token", False) and User.verify_api_token(g.token):
            abort(403, message="You can't use the old token to get a new token.")

        expiration = 3600
        token = g.current_user.generate_api_token(expiration)
        return {"token": token, "expiration": expiration}


def can(name):

    def decorator(func, *args, **kwargs):

        def wraped(*args, **kwargs):
            if g.current_user.permissions.filter_by(name=name).first() is not None:
                return func(*args, **kwargs)

            else:
                abort(403, message="Permission denied.")

        return wraped

    return decorator
