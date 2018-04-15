'''
The config of the blog. If there is a ".env" file in the folder, the application will read the related value in this file and override the default value in the application.
'''
import dotenv
import os

basedir = os.path.abspath(os.path.dirname(__file__))
envpath = os.path.join(basedir, '.env')

if os.path.exists(envpath):
	dotenv.load_dotenv(envpath, override=True)

class BasicConfig():
	SECRET_KEY = os.environ.get("FLASK_SECRET_KEY") or "This is a Secrete key!"
	SQLALCHEMY_TRACK_MODIFICATIONS = False

	@staticmethod
	def init_app(app):
		pass

class DevelopmentConfig(BasicConfig):
	DEBUG = True
	SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URI') or "sqlite:///" + os.path.join(basedir, "data-dev.sqlite")

class TestingConfig(BasicConfig):
	DEBUG = True
	TESTING = True
	WTF_CSRF_ENABLED = False
	WTF_CSRF_CHECK_DEFAULT = False
	SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URI') or "sqlite:///" + os.path.join(basedir, "data-test.sqlite")

config = {
	"development": DevelopmentConfig,
	"testing": TestingConfig,

	"default": TestingConfig
}