'''
Test auth function.
'''
import unittest
from app import create_app, db
from app.models import User

class UserModelTest(unittest.TestCase):
	def setUp(self):
		'''Build the test environment.'''
		self.app = create_app('testing')
		self.app_context = self.app.app_context()
		self.app_context.push()
		db.create_all()

	def tearDown(self):
		'''Clear resource.'''
		self.app_context.pop()
		db.drop_all()

	def test_password_setter(self):
		'''Test models.User.password setter.'''
		user = User(password="test")
		self.assertTrue(user.password_hash is not None)

	def test_password_not_get(self):
		'''Test that that whether the password can get.'''
		user = User(password="test")
		with self.assertRaises(AttributeError):
			user.password

	def test_check_password(self):
		'''Test the password checker.'''
		user = User(password="test")
		self.assertTrue(user.check_password("test"))

	def test_confirmed_token(self):
		'''Test whether the confirmed token can be generated correctly.'''
		user = User(password="test")
		token = user.generate_confirmed_token()
		token_error = "ErrorToken"

		with self.subTest(token=token_error):
			self.assertFalse(user.verify_confirmed_token(token))

		with self.subTest(token=token):
			self.assertTrue(user.verify_confirmed_token(token))

	def test_confirmed_token_expiration(self):
		'''Test the token expiration mechanism.'''
		user = User(password="test")
		token = user.generate_confirmed_token(expiration=0)

		self.assertFalse(user.verify_confirmed_token(token))

if __name__ == '__main__':
	unittest.main()
