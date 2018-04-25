#!/usr/bin/env python3.6
# -*-coding:utf-8-*-
__author__ = "ArianX/arianx.me"
"""
A set of utility tools of managering the blog application.
"""
import os
from flask_migrate import Migrate, migrate, upgrade
from faker import Faker
from random import randint
from app import create_app, db, search
from app.models import User, Post, Comment, Follow, Permission, permissions_dict
from app import config

app = create_app(os.environ.get("FLASK_CONFIG") or "development")
migrate = Migrate(app, db)
fake = Faker()


@app.shell_context_processor
def make_context():
    """
	Add some key components to the line command context to make the debug easier.

	:return: Return a dict which include some context informations.
	"""
    from app import mail
    return dict(
        app=app,
        migrate=migrate,
        db=db,
        User=User,
        Post=Post,
        Comment=Comment,
        Permission=Permission,
        Follow=Follow,
        mail=mail,
        create_app=create_app,
        fake=fake,
        search=search
    )


@app.cli.command()
def create():
    """
	Performing some necessary commands then run a app instance.
	"""
    db.create_all()
    Permission.insert_permissions(permissions_dict)
    app.run()


@app.cli.command()
def fake_user():
    """Generating some random data then insert to the database."""
    if app.config.get("MAIL_SUPPRESS_SEND") != True:
        print("MAIL_SUPPRESS_SEND must be equal to True.")
        return False

    db.create_all()
    Permission.insert_permissions(permissions_dict)
    for a in range(30):
        try:
            email = fake.email()
            username = fake.user_name()
            user = User(
                email=email,
                username=username,
                password="test",
                confirmed=True,
                name=fake.name(),
                age=fake.random_int() % 100,
                location=fake.address(),
                about_me=fake.bs(),
            )
            db.session.add(user)
            db.session.commit()
            print('Generate user "%s":"%s"' % (username, email))
        except:
            db.session.rollback()

    return True


@app.cli.command()
def fake_post():
    """Generating some random data then insert to the database."""
    user_count = User.query.count()
    for b in range(100):
        title = " ".join(fake.words())
        body = "\n".join([fake.text() for a in range(10)])
        post = Post(title=title, body=body)
        post.user = User.query.offset(randint(0, user_count - 1)).first()
        db.session.add(post)
        db.session.commit()
        print('Generate post "%s"' % (post.title))

    return True


@app.cli.command()
def fake_comment():
    """Generating some random comments."""
    post_count = Post.query.count()
    user_count = User.query.count()
    for b in range(500):
        body = " ".join(fake.words())
        comment = Comment(body=body)
        comment.user = User.query.offset(randint(0, user_count - 1)).first()
        comment.post = Post.query.offset(randint(0, post_count - 1)).first()
        db.session.add(comment)
        db.session.commit()

    return True


@app.cli.command()
def fake_follow():
    """Generating some random following relationship."""
    user_count = User.query.count()
    for b in range(500):
        follower = User.query.offset(randint(0, user_count - 1)).first()
        followed = User.query.offset(randint(0, user_count - 1)).first()

        follow_ship = Follow(follower=follower, followed=followed)
        db.session.add(follow_ship)
        db.session.commit()

    return True


@app.cli.command()
def test():
    """
	Add the "test" command to the Flask cli context. It will activate the unittest instance which locates in the tests folder.
	"""
    import unittest

    tests = unittest.TestLoader().discover("tests")
    runner = unittest.TextTestRunner(verbosity=5)
    runner.run(tests)


if __name__ == "__main__":
    app.run()
