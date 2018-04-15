'''
Simplely test the initialize process of the application.
'''
import unittest
from flask import current_app
from app import create_app

class InitialTestCase(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		'''Add app context.'''
		cls.app = create_app('testing')
		cls.app_context = cls.app.app_context()
		cls.app_context.push()

	@classmethod
	def tearDownClass(cls):
		'''Pop app context.'''
		cls.app_context.pop()

	def test_app_exists(self):
		'''Test if the current_app instance exists.'''
		self.assertTrue(current_app is not None)

	def test_test_env(self):
		'''Test if the instance's mod is testing. '''
		self.assertTrue(self.app.config['TESTING'])

if __name__ == '__main__':
	unittest.main()