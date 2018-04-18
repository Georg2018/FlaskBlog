from . import db, bcrypt, login_manager
from flask_login import AnonymousUserMixin, current_user
from flask import current_app, request
import hashlib
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired

class User(db.Model):
	id = db.Column(db.Integer(), primary_key=True)
	_email = db.Column(db.String(128), unique=True, index=True)
	username = db.Column(db.String(128), unique=True, index=True)
	password_hash = db.Column(db.String(128))
	confirmed = db.Column(db.Boolean, default=False)
	active = db.Column(db.Boolean, default=True)

	avatar_url = db.Column(db.String(128), default='')

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
		raise AttributeError('Can\'t get the password palintext.')

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
		serializer = Serializer(current_app.config['SECRET_KEY'], expiration)
		return serializer.dumps({"user_id":self.id}).decode()

	@staticmethod
	def verify_confirmed_token(token):
		serializer = Serializer(current_app.config['SECRET_KEY'])
		try:
			user_id = serializer.loads(token)['user_id']
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
		serializer = Serializer(current_app.config['SECRET_KEY'], expiration)
		return serializer.dumps({'user_id':self.id}).decode()

	@staticmethod
	def verify_resetpass_token(token):
		serializer = Serializer(current_app.config['SECRET_KEY'])

		try:
			user_id = serializer.loads(token)['user_id']
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

	def generate_gravatar_url(self, size=40, default='identicon', rating='x'):
		url = 'http://www.gravatar.com/avatar'
		mail_hash = hashlib.md5(self._email.encode('utf-8')).hexdigest()
		return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(url=url, hash=mail_hash, size=size, default=default, rating=rating)

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

