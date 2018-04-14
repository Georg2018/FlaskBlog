import os
from app import create_app

app = create_app(os.environ.get('FLASK_CONFIG') or 'development')

@app.shell_context_processor
def make_context():
	return dict(context=True, test=test)

@app.cli.command()
def test():
	import unittest

	tests = unittest.TestLoader().discover("tests")
	runner = unittest.TextTestRunner(verbosity=3)
	runner.run(tests)