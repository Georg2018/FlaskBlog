'''
The main component of this blog.
Use `create_app` function to create a app instance.
'''
from flask import Flask
from flask_login import LoginManager, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_moment import Moment
from flask_principal import Principal, Permission, identity_loaded, UserNeed
from flask_pagedown import PageDown
from .config import config

bcrypt = Bcrypt()
db = SQLAlchemy()
mail = Mail()
moment = Moment()
principal = Principal()
pagedown = PageDown()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please login to access this page.'
login_manager.session_protection = 'strong'

def create_app(config_name):
	'''
	To creat a application instance, introduct a name of the config object which locates in the config.py file.
	'''
	app = Flask(__name__)
	app.config.from_object(config[config_name])
	config[config_name].init_app(app)

	bcrypt.init_app(app)
	db.init_app(app)
	login_manager.init_app(app)
	mail.init_app(app)
	moment.init_app(app)
	principal.init_app(app)
	pagedown.init_app(app)

	from .controller import main as main_blueprint
	app.register_blueprint(main_blueprint, template_folder='../templates/main')
	from .controller import auth as auth_blueprint
	app.register_blueprint(auth_blueprint, template_folder='../templates/auth')
	from .controller import api_bp as api_blueprint
	app.register_blueprint(api_blueprint)

	@identity_loaded.connect_via(app)
	def on_identity_loaded(sender, identity):
		identity.user = current_user

		if hasattr(current_user, 'id'):
			identity.provides.add(UserNeed(current_user.id))

		if hasattr(current_user, 'permissions'):
			for pm in current_user.permissions.all():
				identity.provides.add(need(pm.name))

	from .extensions import need
	def has_permission(name):
		'''Used by template to judge whether the user has some permissions.'''
		if Permission(need(name)).can():
			return True
		else:
			return False
	app.add_template_global(has_permission, "has_permission")

	return app

