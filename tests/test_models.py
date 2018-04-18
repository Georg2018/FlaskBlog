'''
Test auth function.
'''
import unittest
from app import create_app, db
from app.models import User
import time
from datetime import datetime
import hashlib

class UserModelTest(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		db.drop_all()

	def setUp(self):
		'''Build the test environment.'''
		self.app = create_app('testing')
		self.app_context = self.app.app_context()
		self.app_context.push()
		db.create_all()

	def tearDown(self):
		'''Clear resource.'''
		self.app_context.pop()
		db.session.remove()
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
		user = User(email="test@test.com", username="test", password="test")
		db.session.add(user)
		db.session.commit()
		token = user.generate_confirmed_token()
		token_error = "ErrorToken"

		with self.subTest(token=token_error):
			self.assertFalse(user.verify_confirmed_token(token_error))

		with self.subTest(token=token):
			self.assertTrue(user.verify_confirmed_token(token))

	def test_confirmed_token_expiration(self):
		'''Test the token expiration mechanism.'''
		user = User(email="test@test.com", username="test", password="test")
		db.session.add(user)
		db.session.commit()
		token = user.generate_confirmed_token(expiration=0)

		time.sleep(1)
		
		self.assertFalse(user.verify_confirmed_token(token))

	def test_resetpass_token(self):
		'''Test the token used by reset pass.'''
		user = User(email="test@test.com", username="test", password="test")
		db.session.add(user)
		db.session.commit()
		
		token = user.generate_resetpass_token()

		with self.subTest(info="error_token"):
			self.assertFalse(user.verify_resetpass_token('error'))

		with self.subTest(info="correct_token"):
			self.assertTrue(user.verify_resetpass_token(token))

	def test_avatar_url(self):
		'''Test the avatar_url generating function.'''
		email = "test@test.com"
		user = User(email=email, username="test", password="test")

		avatar_hash = hashlib.md5(email.encode()).hexdigest()

		self.assertTrue(avatar_hash in user.avatar_url)

	def test_account_member_since(self):
		'''Test the member_since value.'''
		user = User(email="test@test.com", username="test", password="test")
		db.session.add(user)
		db.session.commit()

		self.assertTrue((datetime.utcnow() - user.member_since).total_seconds() < 3)
		self.assertTrue((datetime.utcnow() - user.last_since).total_seconds() < 3)

	def test_account_last_since(self):
		'''Test the updata_last_since function.'''
		user = User(email="test@test.com", username="test", password="test")
		db.session.add(user)
		db.session.commit()

		last = user.last_since
		time.sleep(2)
		now = user.update_last_since()

		self.assertTrue((now-last).total_seconds() > 2)

if __name__ == '__main__':
	unittest.main()
