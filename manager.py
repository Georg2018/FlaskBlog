'''
A set of utility tools of managering the blog application.
'''
import os
from flask_migrate import Migrate, migrate, upgrade
from app import create_app, db
from app.models import User, Permission, permissions_dict
from app import config

app = create_app(os.environ.get('FLASK_CONFIG') or 'development')
migrate = Migrate(app, db)

@app.shell_context_processor
def make_context():
	'''
	Add some key components to the line command context to make the debug easier.

	:return: Return a dict which include some context information.
	'''
	from app import mail
	return dict(app=app, migrate=migrate, db=db, User=User, Permission=Permission, mail=mail, \
		create_app=create_app)

@app.cli.command()
def create():
	'''
	Perform some necessary commands then run a app instance.
	'''
	db.create_all()
	Permission.insert_permissions(permissions_dict)
	app.run()

@app.cli.command()
def test():
	'''
	Add the "test" command to the Flask cli context. It will activate the unittest instance which locates in the tests folder.
	'''
	import unittest
	
	tests = unittest.TestLoader().discover("tests")
	runner = unittest.TextTestRunner(verbosity=5)
	runner.run(tests)

if __name__ == '__main__':
	app.run()