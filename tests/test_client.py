'''
Test basic clien access.
'''
import unittest
from app import create_app, db
from app.models import User

class userAuthTestCase(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		db.drop_all()

	def setUp(self):
		'''Build the test environment.'''
		self.app = create_app('testing')
		self.client = self.app.test_client(use_cookies=True)
		self.app_context = self.app.app_context()
		self.app_context.push()
		db.create_all()

	def tearDown(self):
		'''Clear resource.'''
		self.app_context.pop()
		db.session.remove()
		db.drop_all()

	def test_when_not_login(self):
		'''Test the status of the index page when the user is not logged in.'''
		response = self.client.get('/')
		self.assertEqual(response.status_code, 200)
		self.assertTrue('Hello, Stranger!' in response.get_data(as_text=True))

	def test_login_process(self):
		'''Test the register, login and logout process.'''

		with self.subTest(info="two mismatched passwds when register"):
			response = self.client.post('/auth/register', data={
				"email":"test@test.com",
				"username":"test",
				"password":"12345678",
				"password2":""
				})
			self.assertTrue('The two password must matched.' in response.get_data(as_text=True))

		with self.subTest(info="register"):
			response = self.client.post('/auth/register', data={
				"email":"test@test.com",
				"username":"test",
				"password":"12345678",
				"password2":"12345678"
				}, follow_redirects=True)
			self.assertTrue('You have successfully registered a account.' in response.get_data(as_text=True))


		with self.subTest(info="not confirmed"):
			response = self.client.post('/auth/login', data={
				"identifier":"test@test.com",
				"password":"12345678",
				"remember_me":False
				}, follow_redirects=True)
			self.assertTrue('Unconfirmed' in response.get_data(as_text=True))

		user = User.query.filter_by(username="test").first()
		user.confirmed = True
		db.session.add(user)
		db.session.commit()

		with self.subTest(info="login"):
			response = self.client.post('/auth/login', data={
				"identifier":"test@test.com",
				"password":"12345678",
				"remember_me":False
				}, follow_redirects=True)
			self.assertTrue('Hello, test!' in response.get_data(as_text=True))

		with self.subTest(info="logout"):
			response = self.client.get('/auth/logout', follow_redirects=True)
			self.assertEqual(response.status_code, 200)
			self.assertTrue('Hello, Stranger!' in response.get_data(as_text=True))

	def test_password_change(self):
		'''Test changeing password when know the original password.'''
		user = User(email="test@test.com", username="test", password="12345678")
		user.confirmed = True
		db.session.add(user)
		db.session.commit()

		response = self.client.post('/auth/login', data={
			"identifier":"test@test.com",
			"password":"12345678",
			"remember_me":False
			}, follow_redirects=True)
		self.assertTrue('Hello, test!' in response.get_data(as_text=True))

		response = self.client.post('/auth/changepass', data={
			"old_password":"12345678",
			"new_password":"87654321",
			"new_password2":"87654321"
			}, follow_redirects=True)
		self.assertTrue('successfully' in response.get_data(as_text=True))

		response = self.client.post('/auth/login', data={
			"identifier":"test@test.com",
			"password":"87654321",
			"remember_me":False
			}, follow_redirects=True)
		self.assertTrue('Hello, test!' in response.get_data(as_text=True))

	def test_change_email(self):
		'''Test changing email.'''
		user = User(email="test@test.com", username="test", password="12345678")
		user.confirmed= True
		db.session.add(user)
		db.session.commit()

		response = self.client.post('/auth/login', data={
			"identifier":"test",
			"password":"12345678",
			"remember_me":False
			}, follow_redirects=True)
		self.assertTrue('Hello, test!' in response.get_data(as_text=True))

		response = self.client.post('/auth/changemail', data={
			"password":"12345678",
			"new_email":"new@email.com"
			}, follow_redirects=True)
		self.assertTrue('Unconfirmed.' in response.get_data(as_text=True))

		user.confirmed = True
		db.session.add(user)
		db.session.commit()

		response = self.client.get('/')
		self.assertTrue('Hello' in response.get_data(as_text=True))

	def test_reset_password(self):
		'''Test resetting password.'''
		user = User(email='test@test.com', username='test', password="12345678")
		db.session.add(user)
		db.session.commit()

		response = self.client.post('/auth/authresetpass', data={
			"username":"test"
			}, follow_redirects=True)
		self.assertTrue('We have seet a mail to you.' in response.get_data(as_text=True))

		token = user.generate_resetpass_token()
		response = self.client.post('/auth/resetpass/'+token, data={
			"password":"87654321"
			}, follow_redirects=True)

		self.assertTrue('You have successfully resert your password.' in response.get_data(as_text=True))

if __name__ == '__main__':
	unittest.main()