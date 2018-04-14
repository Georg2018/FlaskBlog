'''
The main component of this blog.
Use `create_app` function to create a app instance.
'''
from flask import Flask
from .config import config


def create_app(config_name):
	'''
	To creat a application instance, import a name of the config object which locates in the config.py file.
	'''
	app = Flask(__name__)
	app.config.from_object(config[config_name])
	config[config_name].init_app(app)

	from .controller import main as main_blueprint
	app.register_blueprint(main_blueprint, template_folder='../templates/main')

	return app