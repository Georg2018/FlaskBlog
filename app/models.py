from . import db, bcrypt, login_manager, search
from flask_login import AnonymousUserMixin, current_user
from flask_principal import Permission as pm, Need
from flask import current_app, request
import hashlib
from datetime import datetime
from itsdangerous import (
    TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired
)
from markdown import markdown
import bleach

tags = db.Table(
    "tags",
    db.Column("tag_id", db.Integer, db.ForeignKey("tag.id")),
    db.Column("post_id", db.Integer, db.ForeignKey("post.id")),
)

permissions = db.Table(
    "permissions",
    db.Column("permission_id", db.Integer, db.ForeignKey("permission.id")),
    db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
)

permissions_dict = {
    "admin": ["Do anythings.", False],
    "post": ["Can publish blog.", True],
    "comment": ["Can add comment.", True],
    "follow": ["Follow user.", True],
    "editinfo": ["Edit the user's own information.", True],
}


class Permission(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False, index=True)
    description = db.Column(db.String(128))
    default = db.Column(db.Boolean, default=True)

    @staticmethod
    def insert_permissions(permissions):
        for name, detail in permissions.items():
            try:
                role = Permission(name=name, description=detail[0], default=detail[1])
                db.session.add(role)
                db.session.commit()
            except:
                db.session.rollback()


class Follow(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    follower_id = db.Column(db.Integer(), db.ForeignKey("user.id"))
    followed_id = db.Column(db.Integer(), db.ForeignKey("user.id"))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class User(db.Model):
    """
	Notice: Becauser the email is implemented by the property, you can\'t filter the
	 email in the User.query. Use _email field to filter in the query instead.
	"""
    id = db.Column(db.Integer(), primary_key=True)
    _email = db.Column(db.String(128), unique=True, index=True)
    username = db.Column(db.String(128), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    active = db.Column(db.Boolean, default=True)

    name = db.Column(db.String(64))
    age = db.Column(db.Integer())
    location = db.Column(db.String(128))
    about_me = db.Column(db.Text())
    avatar_url = db.Column(db.String(128), default="")

    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_since = db.Column(db.DateTime(), default=datetime.utcnow)

    permissions = db.relationship(
        "Permission",
        secondary=permissions,
        backref=db.backref("users", lazy="dynamic"),
        lazy="dynamic",
    )

    posts = db.relationship("Post", backref="user", lazy="dynamic")

    comments = db.relationship("Comment", backref="user", lazy="dynamic")

    followers = db.relationship(
        "Follow",
        foreign_keys=[Follow.followed_id],
        backref=db.backref("followed", lazy="joined"),
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    followings = db.relationship(
        "Follow",
        foreign_keys=[Follow.follower_id],
        backref=db.backref("follower", lazy="joined"),
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    def __init__(self, *arg, **kwargs):
        """Add all of the default roles for the user when create a instance."""
        list(
            map(
                lambda role: self.permissions.append(role),
                Permission.query.filter_by(default=True).all(),
            )
        )

        if kwargs.get("email") == current_app.config.get("FLASK_ADMIN"):
            self.permissions.append(Permission.query.filter_by(name="admin").first())

        db.session.add(self)
        db.session.commit()

        super(User, self).__init__(*arg, **kwargs)

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, new_email):
        old_email = self._email
        self._email = new_email

        if old_email != new_email:
            self.avatar_url = self.generate_gravatar_url()

    @property
    def password(self):
        raise AttributeError("Can't get the password palintext.")

    @password.setter
    def password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password)

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    @property
    def is_active(self):
        return self.active

    @is_active.setter
    def is_active(self, value):
        self.active = value
        return self.active

    def get_id(self):
        return str(self.id)

    def generate_confirmed_token(self, expiration=600):
        serializer = Serializer(current_app.config["SECRET_KEY"], expiration)
        return serializer.dumps({"user_id": self.id}).decode()

    @staticmethod
    def verify_confirmed_token(token):
        serializer = Serializer(current_app.config["SECRET_KEY"])
        try:
            user_id = serializer.loads(token)["user_id"]
        except BadSignature:
            return False

        except SignatrueExpired:
            return False

        try:
            user = User.query.get(user_id)
        except:
            return False

        if user is not None and not user.confirmed:
            user.confirmed = True
            db.session.add(user)
            db.session.commit()
            return user

        else:
            return False

    def generate_resetpass_token(self, expiration=300):
        serializer = Serializer(current_app.config["SECRET_KEY"], expiration)
        return serializer.dumps({"user_id": self.id}).decode()

    @staticmethod
    def verify_resetpass_token(token):
        serializer = Serializer(current_app.config["SECRET_KEY"])

        try:
            user_id = serializer.loads(token)["user_id"]
        except BadSignature:
            return False

        except SignatureExpired:
            return False

        try:
            user = User.query.get(user_id)
        except:
            return False

        if user is not None:
            return user

        else:
            return False

    def generate_api_token(self, expiration=300):
        serializer = Serializer(current_app.config["SECRET_KEY"], expiration)
        return serializer.dumps({"user_id": self.id}).decode()

    @staticmethod
    def verify_api_token(token):
        serializer = Serializer(current_app.config["SECRET_KEY"])

        try:
            user_id = serializer.loads(token)["user_id"]
        except BadSignature:
            return False

        except SignatureExpired:
            return False

        try:
            user = User.query.get(user_id)
        except:
            return False

        if user is not None:
            return user

        else:
            return False

    def generate_gravatar_url(self, size=150, default="identicon", rating="x"):
        url = "http://www.gravatar.com/avatar"
        mail_hash = hashlib.md5(self._email.encode("utf-8")).hexdigest()
        return "{url}/{hash}?s={size}&d={default}&r={rating}".format(
            url=url, hash=mail_hash, size=size, default=default, rating=rating
        )

    def update_last_since(self):
        self.last_since = datetime.utcnow()
        db.session.add(self)
        db.session.commit()

        return self.last_since

    def can(self, name):
        if pm(Need("permission", name)).can():
            return True

        return False

    def is_followed_user(self, userid):
        if self.followings.filter_by(followed_id=userid).first() is not None:
            return True

        else:
            return False

    def is_followed_by(self, userid):
        if self.followers.filter_by(follower_id=userid).first() is not None:
            return True

        else:
            return False

    def follow(self, userid):
        follow_ship = Follow(followed_id=userid, follower_id=self.id)
        db.session.add(follow_ship)
        db.session.commit()
        return True

    def unfollow(self, userid):
        follow_ship = Follow.query.filter_by(
            followed_id=userid, follower_id=self.id
        ).first()
        if follow_ship:
            db.session.delete(follow_ship)
            db.session.commit()
            return True

        return False

    @property
    def followed_posts(self):
        posts = Post.query.join(Follow, Follow.followed_id == Post.user_id).filter(
            Follow.follower_id == self.id
        ).order_by(
            Post.timestamp.desc()
        )
        return posts


class AnonymousUser():

    @property
    def is_authenticated(self):
        return False

    @property
    def is_anonymous(self):
        return True

    @property
    def is_active(self):
        return False

    def get_id(self):
        return None


login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Post(db.Model):
    __searchable__ = ["title", "html"]

    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(
        db.String(128), nullable=False, default="Unknow title", index=True
    )
    body = db.Column(db.Text)
    html = db.Column(db.Text)

    comments = db.relationship("Comment", backref="post", lazy="dynamic")

    disable = db.Column(db.Boolean, default=False)

    timestamp = db.Column(db.DateTime(), default=datetime.utcnow)

    user_id = db.Column(db.Integer(), db.ForeignKey("user.id"))

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = [
            "a",
            "abbr",
            "acronym",
            "b",
            "blockquote",
            "code",
            "em",
            "i",
            "li",
            "ol",
            "pre",
            "strong",
            "ul",
            "h1",
            "h2",
            "h3",
            "p",
            "img",
        ]
        target.html = bleach.linkify(
            bleach.clean(
                markdown(value, output_format="html"), tags=allowed_tags, strip=True
            )
        )

        # search.update_index()


db.event.listen(Post.body, "set", Post.on_changed_body)


class Tag(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(16), nullable=False, unique=True, index=True)

    posts = db.relationship(
        "Post",
        secondary=tags,
        backref=db.backref("tags", lazy="joined"),
        lazy="dynamic",
    )


class Comment(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    body = db.Column(db.String(512), nullable=False, index=True)

    disable = db.Column(db.Boolean, default=False)

    user_id = db.Column(db.Integer(), db.ForeignKey("user.id"))
    post_id = db.Column(db.Integer(), db.ForeignKey("post.id"))

    timestamp = db.Column(db.DateTime(), default=datetime.utcnow)
