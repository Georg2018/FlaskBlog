'''
The main component of this blog.
Use `create_app` function to create a app instance.
'''
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_moment import Moment
from .config import config

bcrypt = Bcrypt()
db = SQLAlchemy()
mail = Mail()
moment = Moment()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please login to access this page.'
login_manager.session_protection = 'strong'

def create_app(config_name):
	'''
	To creat a application instance, import a name of the config object which locates in the config.py file.
	'''
	app = Flask(__name__)
	app.config.from_object(config[config_name])
	config[config_name].init_app(app)

	bcrypt.init_app(app)
	db.init_app(app)
	login_manager.init_app(app)
	mail.init_app(app)
	moment.init_app(app)

	from .controller import main as main_blueprint
	app.register_blueprint(main_blueprint, template_folder='../templates/main')
	from .controller import auth as auth_blueprint
	app.register_blueprint(auth_blueprint, template_folder='../templates/auth')

	return app