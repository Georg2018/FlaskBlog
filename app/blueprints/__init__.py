from flask import Blueprint

main_blueprint = Blueprint('main', __name__, url_prefix='/', template_folder='../templates/main', static_folder='../static')
from .main import view

