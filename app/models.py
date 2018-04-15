from . import db, bcrypt, login_manager
from flask_login import AnonymousUserMixin, current_user
from flask import current_app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired

class User(db.Model):
	id = db.Column(db.Integer(), primary_key=True)
	email = db.Column(db.String(128), unique=True, index=True)
	username = db.Column(db.String(128), unique=True, index=True)
	password_hash = db.Column(db.String(128))
	confirmed = db.Column(db.Boolean, default=False)

	@property
	def password(self):
		raise AttributeError('Can\'t get the password palintext.')

	@password.setter
	def password(self, password):
		self.password_hash = bcrypt.generate_password_hash(password)

	def check_password(self, password):
		return bcrypt.check_password_hash(self.password_hash, password)

	def is_authenticated(self):
		if isinstance(self, AnonymousUserMixin):
			return False
		else:
			return True

	def is_anonymous(self):
		if isinstance(self, AnonymousUserMixin):
			return True
		else:
			return False

	def is_active(self):
		return True

	def get_id(self):
		return str(self.id)

	def generate_confirmed_token(self, expiration=600):
		serializer = Serializer(current_app.config['SECRET_KEY'], expiration)
		return serializer.dumps({"user_id":self.id}).decode()

	@staticmethod
	def verify_confirmed_token(token):
		serializer = Serializer(current_app.config['SECRET_KEY'])
		try:
			user_id = serializer.loads(token)
		except BadSignature:
			return False
		except SignatrueExpired:
			return False

		user = User.query.get(id=user_id)

		if user is not None and not user.confirmed:
			user.confirmed = True
			db.session.add(user)
			db.session.commit()
			return user.id
		else:
			return False

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

