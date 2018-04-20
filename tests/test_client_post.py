import unittest
from flask import url_for
from app import create_app
from app.models import User, Post, Permission, db, permissions_dict

class PostPagesTestCase(unittest.TestCase):
	'''Test the pages about post.'''
	@classmethod
	def setUpClass(cls):
		db.drop_all()

	def setUp(self):
		self.app = create_app('testing')
		self.client = self.app.test_client(use_cookies=True)
		self.app_context = self.app.app_context()
		self.app_context.push()
		self.request_context = self.app.test_request_context()
		self.request_context.push()
		db.create_all()
		Permission.insert_permissions(permissions_dict)

	def tearDown(self):
		self.app_context.pop()
		self.request_context.pop()
		db.drop_all()

	def test_post_submit(self):
		user = User(email="test@test.com", username="test", password="test")
		user.confirmed = True
		db.session.add(user)
		db.session.commit()

		response = self.client.post(url_for('auth.login'), data={
			'identifier':"test",
			"password":"test",
			"remember_me":"False"
			}, follow_redirects=True)
		self.assertTrue('Hello, test!' in response.get_data(as_text=True))

		response = self.client.post(url_for('main.post_submit'), data={
			"title":"1234",
			"body":"test"
			}, follow_redirects=True)
		self.assertTrue('You have successfully submited a article.' in response.get_data(as_text=True))

		response = self.client.get(url_for('main.post', postid=user.posts.all()[0].id), follow_redirects=True)
		self.assertTrue('test' in response.get_data(as_text=True))

	def test_post_edit(self):
		user = User(email="test@test.com", username="test", password="test")
		user.confirmed = True
		post = Post(title="1234", body="none")
		post.user = user
		db.session.add(user)
		db.session.add(post)
		db.session.commit()

		response = self.client.post(url_for('auth.login'), data={
			"identifier":"test",
			"password":"test"
			}, follow_redirects=True)
		self.assertTrue('test' in response.get_data(as_text=True))

		response = self.client.post(url_for('main.post_edit', postid=post.id), data={
			"title":"1234",
			"body":"test_edit"
			}, follow_redirects=True)
		self.assertTrue('test_edit' in response.get_data(as_text=True))