'''
A set of utility tools of managering the blog application.
'''
import os
from app import create_app

app = create_app(os.environ.get('FLASK_CONFIG') or 'development')

@app.shell_context_processor
def make_context():
	'''
	Add some key components to the line command context to make the debug easier.

	:return: Return a dict which include some context information.
	'''
	return dict(test=test)

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