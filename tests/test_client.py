'''
Test basic clien access.
'''
import unittest
from app import create_app, db
from app.models import User

class userAuthTestCase(unittest.TestCase):
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

		#two mismatched passwds when register
		response = self.client.post('/auth/register', data={
			"email":"test@test.com",
			"username":"test",
			"password":"12345678",
			"password2":""
			})
		self.assertTrue('The two password must match.' in response.get_data(as_text=True))

		#register
		response = self.client.post('/auth/register', data={
			"email":"test@test.com",
			"username":"test",
			"password":"12345678",
			"password2":"12345678"
			}, follow_redirects=True)
		self.assertTrue('You have successfully registered a account.' in response.get_data(as_text=True))

		user = User.query.filter_by(username="test").first()
		user.confirmed = True
		db.session.add(user)
		db.session.commit()

		#login
		response = self.client.post('/auth/login', data={
			"identifier":"test@test.com",
			"password":"12345678",
			"remember_me":False
			}, follow_redirects=True)
		self.assertTrue('Hello, test!' in response.get_data(as_text=True))

		#loginout
		response = self.client.get('/auth/logout', follow_redirects=True)
		self.assertEqual(response.status_code, 200)
		self.assertTrue('Hello, Stranger!' in response.get_data(as_text=True))

if __name__ == '__main__':
	unittest.main()