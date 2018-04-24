"""
Test auth function.
"""
import unittest
from app import create_app, db
from app.models import User, Post, Follow, Permission, permissions_dict
import time
from datetime import datetime
import hashlib


class UserModelTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        db.drop_all()

    def setUp(self):
        """Build the test environment."""
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        """Clear resource."""
        self.app_context.pop()
        db.session.remove()
        db.drop_all()

    def test_password_setter(self):
        """Test models.User.password setter."""
        user = User(password="test")
        self.assertTrue(user.password_hash is not None)

    def test_password_not_get(self):
        """Test that that whether the password can get."""
        user = User(password="test")
        with self.assertRaises(AttributeError):
            user.password

    def test_check_password(self):
        """Test the password checker."""
        user = User(password="test")
        self.assertTrue(user.check_password("test"))

    def test_confirmed_token(self):
        """Test whether the confirmed token can be generated correctly."""
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
        """Test the token expiration mechanism."""
        user = User(email="test@test.com", username="test", password="test")
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmed_token(expiration=0)

        time.sleep(1)

        self.assertFalse(user.verify_confirmed_token(token))

    def test_resetpass_token(self):
        """Test the token used by reset pass."""
        user = User(email="test@test.com", username="test", password="test")
        db.session.add(user)
        db.session.commit()

        token = user.generate_resetpass_token()

        with self.subTest(info="error_token"):
            self.assertFalse(user.verify_resetpass_token("error"))

        with self.subTest(info="correct_token"):
            self.assertTrue(user.verify_resetpass_token(token))

    def test_avatar_url(self):
        """Test the avatar_url generating function."""
        email = "test@test.com"
        user = User(email=email, username="test", password="test")

        avatar_hash = hashlib.md5(email.encode()).hexdigest()

        self.assertTrue(avatar_hash in user.avatar_url)

    def test_account_member_since(self):
        """Test the member_since value."""
        user = User(email="test@test.com", username="test", password="test")
        db.session.add(user)
        db.session.commit()

        self.assertTrue((datetime.utcnow() - user.member_since).total_seconds() < 3)
        self.assertTrue((datetime.utcnow() - user.last_since).total_seconds() < 3)

    def test_account_last_since(self):
        """Test the updata_last_since function."""
        user = User(email="test@test.com", username="test", password="test")
        db.session.add(user)
        db.session.commit()

        last = user.last_since
        time.sleep(2)
        now = user.update_last_since()

        self.assertTrue((now - last).total_seconds() > 2)


class PermissionModelTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        db.drop_all()

    def setUp(self):
        """Build the test environment."""
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        """Clear resource."""
        self.app_context.pop()
        db.session.remove()
        db.drop_all()

    def test_insert_permissions(self):
        """Test inserting permissions to the Permission Model."""
        Permission.insert_permissions(permissions_dict)

        self.assertTrue(len(permissions_dict) == len(Permission.query.all()))

    def test_user_permission_relationship(self):
        """Test that whether both of the User Model and Permission Model has correct relationship."""
        user1 = User(email="test1@test.com", username="test1", password="test1")
        user2 = User(email="test2@test.com", username="test2", password="test2")
        Permission.insert_permissions(permissions_dict)
        per1, per2 = Permission.query.get(1), Permission.query.get(2)
        user1.permissions.append(per1)
        user1.permissions.append(per2)
        user2.permissions.append(per1)
        db.session.add(user1, user2)
        db.session.commit()

        self.assertTrue(len(user1.permissions.all()) == 2)
        self.assertTrue(len(user2.permissions.all()) == 1)
        self.assertTrue(len(per1.users.all()) == 2)
        self.assertTrue(len(per2.users.all()) == 1)

        self.assertTrue(per1 in user1.permissions.all())
        self.assertTrue(user1 in per2.users.all())
        self.assertTrue(user2 in per1.users.all())


class PostModelTest(unittest.TestCase):
    """Test the Post model."""

    @classmethod
    def setUpClass(cls):
        db.drop_all()

    def setUp(self):
        """Build the test environment."""
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        """Clear resource."""
        self.app_context.pop()
        db.session.remove()
        db.drop_all()

    def test_on_change_body(self):
        """Test the whether clear the tags when commit a article."""
        post = Post(title="test", body="<script></script><p></p>")

        self.assertFalse("<script>" in post.html)
        self.assertTrue("<p>" in post.html)


class FollowModelTest(unittest.TestCase):
    """Test the Follow model."""

    @classmethod
    def setUpClass(cls):
        db.drop_all()

    def setUp(self):
        """Build the test environment."""
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        """Clear resource."""
        self.app_context.pop()
        db.session.remove()
        db.drop_all()

    def test_is_followed_user(self):
        user1 = User(email="test@test1.com", username="test1", password="test")
        user2 = User(email="test@test2.com", username="test2", password="test")
        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()

        user1.follow(user2.id)

        self.assertTrue(user1.is_followed_user(user2.id))

    def test_is_followed_by(self):
        user1 = User(email="test@test1.com", username="test1", password="test")
        user2 = User(email="test@test2.com", username="test2", password="test")
        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()

        user1.follow(user2.id)

        self.assertTrue(user2.is_followed_by(user1.id))


if __name__ == "__main__":
    unittest.main()
