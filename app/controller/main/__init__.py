'''
The blog's main blueprint. Contain the logic of publishing, modifying, and displaying the blog.
'''
from flask import Blueprint

main = Blueprint('main', __name__)
from . import view, errors