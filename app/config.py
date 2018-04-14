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