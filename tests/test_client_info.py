import unittest
from flask import url_for
from app import create_app, db
from app.models import User, Permission, permissions_dict

class InfoPagesTestCase(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		db.drop_all()

	def setUp(self):
		'''Build the test environment.'''
		self.app = create_app('testing')
		self.client = self.app.test_client(use_cookies=True)
		self.app_context = self.app.app_context()
		self.app_context.push()
		self.request_context = self.app.test_request_context()
		self.request_context.push()
		db.create_all()

	def tearDown(self):
		'''Clear resource.'''
		self.app_context.pop()
		self.request_context.pop()
		db.session.remove()
		db.drop_all()

	def test_change_user_info(self):
		'''Test change user info.'''
		Permission.insert_permissions(permissions_dict)
		user = User(email="test@test.com", username="test", password="12345678")
		user.confirmed = True
		db.session.add(user)
		db.session.commit()

		response = self.client.post(url_for('auth.login'), data={
			"identifier":"test",
			"password":"12345678",
			"remember_me":"False"
			}, follow_redirects=True)
		self.assertTrue('Hello, test!' in response.get_data(as_text=True))

		response = self.client.post(url_for('main.user_info_edit'), data={
			"name":"mike",
			"age":"15",
			"location":"China",
			"about_me":"hi"
			}, follow_redirects=True)
		self.assertTrue('You have successfully updated your profile.' in response.get_data(as_text=True))

	def test_admin(self):
		'''Test the default admin account whether it can be set correctly.'''
		Permission.insert_permissions(permissions_dict)
		user = User(email=self.app.config.get('FLASK_ADMIN'), username="test", password="12345678")
		user.confirmed = False
		db.session.add(user)
		db.session.commit()

		response = self.client.post(url_for('auth.login'), data={
			"identifier":"test",
			"password":"12345678",
			"remember_me":"False"
			}, follow_redirects=True)
		self.assertTrue('Hello, test!' in response.get_data(as_text=True))

	def test_admin_promote(self):
		'''Test the whether a admin account can promote another normal account to a admin account.'''
		Permission.insert_permissions(permissions_dict)
		admin_user = User(email=self.app.config.get('FLASK_ADMIN'), username='admin', password="12345678")
		admin_user.confirmed = True
		db.session.add(admin_user)
		db.session.commit()

		normal_user = User(email="test@test.com", username="test", password="12345678")
		normal_user.confirmed = True
		db.session.add(normal_user)
		db.session.commit()

		response = self.client.post(url_for('auth.login'), data={
			"identifier":"admin",
			"password":"12345678",
			"remember_me":"False"
			}, follow_redirects=True)
		self.assertTrue("Hello, admin!" in response.get_data(as_text=True))

		response = self.client.post(url_for('main.admin_info_edit', username='test'), data={
			"email":"test@test.com",
			"username":"test",
			"permission":["admin"]
			}, follow_redirects=True)
		self.assertTrue("Updata successfully." in response.get_data(as_text=True))

if __name__ == '__main__':
	unittest.main()