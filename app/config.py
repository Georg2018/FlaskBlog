'''
The config of the blog. If there is a ".env" file in the folder, the application will read the related value in this file and override the default value in the application.
'''
import dotenv
import os

basedir = os.path.abspath(os.path.dirname(__file__))
envpath = os.path.join(basedir, '../.env')

if os.path.exists(envpath):
	dotenv.load_dotenv(envpath, override=True)

class BasicConfig():
	SECRET_KEY = os.environ.get("FLASK_SECRET_KEY") or "This is a Secrete key!"

	@staticmethod
	def init_app(app):
		pass

class DevelopmentConfig(BasicConfig):
	DEBUG = True

class TestingConfig(BasicConfig):
	TESTING = True
	WTF_CSRF_ENABLED = False

config = {
	"development": DevelopmentConfig,
	"testing": TestingConfig,

	"default": TestingConfig
}