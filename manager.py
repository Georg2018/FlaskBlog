'''
A set of utility tools of managering the blog application.
'''
import os
from flask_migrate import Migrate, upgrade
from app import create_app, db
from app.models import User

app = create_app(os.environ.get('FLASK_CONFIG') or 'testing')
migrate = Migrate(app, db)

@app.shell_context_processor
def make_context():
	'''
	Add some key components to the line command context to make the debug easier.

	:return: Return a dict which include some context information.
	'''
	from app import mail
	return dict(app=app, migrate=migrate, db=db, User=User, mail=mail)

@app.cli.command()
def create():
	db.create_all()
	app.run()

@app.cli.command()
def test():
	'''
	Add the "test" command to the Flask cli context. It will activate the unittest instance which locates in the tests folder.
	'''
	import unittest

	tests = unittest.TestLoader().discover("tests")
	runner = unittest.TextTestRunner(verbosity=3)
	runner.run(tests)

if __name__ == '__main__':
	app.run()