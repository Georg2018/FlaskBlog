'''
The main blueprint's view. Defined the route of the main blueprint and the related logic.
'''
from flask import render_template, url_for
from flask_login import current_user, login_required
from . import main

@main.route('/')
def index():
	return render_template('main/index.html')