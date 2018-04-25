import unittest
import base64
import json
from app import create_app, db
from app.models import User, Post, Comment, Follow, Permission, permissions_dict

class UserApiTestCase(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		db.drop_all()

	def setUp(self):
		self.app = create_app('testing')
		self.app_context = self.app.app_context()
		self.app_context.push()
		self.client = self.app.test_client()
		db.create_all()
		Permission.insert_permissions(permissions_dict)

	def tearDown(self):
		db.drop_all()
		self.app_context.pop()

	def open_with_auth(self, url, method, username, password, data):
		auth = username + ':' + password
		auth = auth.encode()
		res = self.client.open(url,
			method=method,
			headers={
				'Authorization': 'Basic ' + base64.b64encode(auth).decode()
			},
			data=data
		)
		return json.loads(res.data)

	def test_user_get(self):
		user = User(email="test@test.com", username="test", password="test")
		user.confirmed = True
		db.session.add(user)
		db.session.commit()

		res = self.client.get('api/user/'+str(user.username))
		res = json.loads(res.data)
		self.assertTrue(user.id == res['id'])

	def test_users(self):
		user1 = User(email="test1@test.com", username="test1", password="test")
		user2 = User(email="test2@test.com", username="test2", password="test")
		db.session.add(user1)
		db.session.add(user2)
		db.session.commit()

		res = self.client.get('api/users')
		res = json.loads(res.data)
		self.assertTrue(res['all_users'] == 2)

	def test_user_edit(self):
		user = User(email="test@test.com", username="test", password="test")
		db.session.add(user)
		db.session.commit()

		res = self.open_with_auth('api/user/'+str(user.username),
			"post",
			"test",
			"test",
			{"name":"mike"}
		)
		self.assertTrue(res["realname"] == "mike" )

	def test_user_follow(self):
		user1 = User(email="test1@test.com", username="test1", password="test")
		user2 = User(email="test2@test.com", username="test2", password="test")
		db.session.add(user1)
		db.session.add(user2)
		db.session.commit()

		follow = Follow(follower_id=user1.id, followed_id=user2.id)
		db.session.add(follow)
		db.session.commit()

		res = self.client.get('api/user/'+str(user2.username)+'/followers')
		res = json.loads(res.data)
		self.assertTrue(res['all_users'] == 1)

		res = self.client.get('api/user/'+str(user1.username)+'/followings')
		res = json.loads(res.data)
		self.assertTrue(res['all_users'] == 1)


class PostApiTestCase(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		db.drop_all()

	def setUp(self):
		self.app = create_app('testing')
		self.app_context = self.app.app_context()
		self.app_context.push()
		self.client = self.app.test_client()
		db.create_all()
		Permission.insert_permissions(permissions_dict)

	def tearDown(self):
		self.app_context.pop()
		db.drop_all()

	def open_with_auth(self, url, method, username, password, data=None):
		auth = username + ':' + password
		auth = auth.encode()
		if data:
			res = self.client.open(url,
				method=method,
				headers={
					'Authorization': 'Basic ' + base64.b64encode(auth).decode()
				},
				data=data
			)
		else:
			res = self.client.open(url,
				method=method,
				headers={
					'Authorization': 'Basic ' + base64.b64encode(auth).decode()
				},
			)
		return json.loads(res.data)

	def test_post_get(self):
		user = User(email="test@test.com", username="test", password="test")
		db.session.add(user)
		db.session.commit()

		post = Post(title="test", body="test")
		post.user = user
		db.session.add(post)
		db.session.commit()

		res = self.client.get('api/post/'+str(post.id))
		res = json.loads(res.data)

		self.assertTrue( res['id'] == post.id )

	def test_posts_get(self):
		user = User(email="test@test.com", username="test", password="test")
		db.session.add(user)
		db.session.commit()

		post1 = Post(title="test1", body="test")
		post2 = Post(title="test2", body="test")
		db.session.add(post1)
		db.session.add(post2)
		db.session.commit()

		res = self.client.get('api/posts')
		res = json.loads(res.data)

		self.assertTrue( res['all_posts'] == 2)

	def test_post_put(self):
		user = User(email="test@test.com", username="test", password="test")
		db.session.add(user)
		db.session.commit()

		res = self.open_with_auth('api/post', 
			"put",
			"test",
			"test",
			{
				"title":"test",
				"body":"test"
			}
			)
		self.assertTrue(res['title'] == 'test')

	def test_post_post(self):
		user = User(email="test@test.com", username="test", password="test")
		db.session.add(user)
		db.session.commit()

		post = Post(title="test", body="test")
		post.user = user
		db.session.add(post)
		db.session.commit()

		res = self.client.get('api/post/'+str(post.id))
		res = json.loads(res.data)
		self.assertTrue(res['title'] == 'test')

		res = self.open_with_auth('api/post/'+str(post.id),
			'post',
			'test',
			'test',
			{
				"title":"put_test",
				"body":"put_test",
			})
		self.assertTrue(res['title'] == "put_test")

	def test_followed_posts(self):
		user1 = User(email="test1@test.com", username="test1", password="test")
		user2 = User(email="test2@test.com", username="test2", password="test")
		db.session.add(user1)
		db.session.add(user2)
		db.session.commit()

		post = Post(title="test", body="test")
		post.user = user2
		db.session.add(post)
		db.session.commit()

		follow = Follow(follower_id=user1.id, followed_id=user2.id)
		db.session.add(follow)
		db.session.commit()

		res = self.open_with_auth("api/followedposts",
			"get",
			"test1",
			"test",
			)
		self.assertTrue(res['all_posts'] == 1)

	def test_users_posts(self):
		user = User(email="test@test.com", username="test", password="test")
		db.session.add(user)
		db.session.commit()

		post = Post(title="test", body="test")
		post.user = user
		db.session.add(post)
		db.session.commit()

		res = self.client.get('api/user/%s/posts'%(user.username))
		res = json.loads(res.data)
		self.assertTrue(res['all_posts'] == 1)

class CommentApiTest(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		db.drop_all()

	def setUp(self):
		self.app = create_app('testing')
		self.app_context = self.app.app_context()
		self.app_context.push()
		self.client = self.app.test_client()
		db.create_all()
		Permission.insert_permissions(permissions_dict)

	def tearDown(self):
		self.app_context.pop()
		db.drop_all()

	def open_with_auth(self, url, method, username, password, data=None):
		auth = username + ':' + password
		auth = auth.encode()
		if data:
			res = self.client.open(url,
				method=method,
				headers={
					'Authorization': 'Basic ' + base64.b64encode(auth).decode()
				},
				data=data
			)
		else:
			res = self.client.open(url,
				method=method,
				headers={
					'Authorization': 'Basic ' + base64.b64encode(auth).decode()
				},
			)
		return json.loads(res.data)

	def test_comment_get(self):
		user = User(email="test@test.com", username="test", password="test")
		db.session.add(user)
		db.session.commit()

		post = Post(title="test", body="test")
		post.user = user
		db.session.add(post)
		db.session.commit()

		comment = Comment(body="test")
		comment.user = user
		comment.post = post
		db.session.add(comment)
		db.session.commit()

		res = self.client.get('api/comment/%d'%(comment.id))
		res = json.loads(res.data)
		self.assertTrue( res['id'] == comment.id )

	def test_post_comments_get(self):
		user = User(email="test@test.com", username="test", password="test")
		db.session.add(user)
		db.session.commit()

		post = Post(title="test", body="test")
		post.user = user
		db.session.add(post)
		db.session.commit()

		comment = Comment(body="test")
		comment.user = user
		comment.post = post
		db.session.add(comment)
		db.session.commit()

		res = self.client.get('api/post/%d/comments'%(post.id))
		res = json.loads(res.data)
		self.assertTrue(res['all_comments'] == 1)

	def test_comment_put(self):
		user = User(email="test@test.com", username="test", password="test")
		db.session.add(user)
		db.session.commit()

		post = Post(title="test", body="test")
		post.user = user
		db.session.add(post)
		db.session.commit()

		res = self.open_with_auth('api/post/%d/comments'%(post.id),
			"put",
			"test",
			"test",
			{"body":"test"},
			)
		self.assertTrue(res["body"] == "test")

	def test_comment_post(self):
		user = User(email="test@test.com", username="test", password="test")
		db.session.add(user)
		db.session.commit()

		post = Post(title="test", body="test")
		post.user = user
		db.session.add(post)
		db.session.commit()

		comment = Comment(body="test")
		comment.user = user
		comment.post = post
		db.session.add(comment)
		db.session.commit()

		res = self.client.get('api/comment/%d'%(comment.id))
		res = json.loads(res.data)
		self.assertTrue(res['article_id'] == post.id)

		res = self.open_with_auth('api/comment/%d'%(comment.id),
			"post",
			"test",
			"test",
			{"body":"post_test"}
			)
		self.assertTrue(res["body"] == "post_test")


if __name__ == '__main__':
	unittest.main()