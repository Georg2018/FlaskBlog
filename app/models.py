from . import db, bcrypt, login_manager
from flask_login import AnonymousUserMixin

class User(db.Model):
	id = db.Column(db.Integer(), primary_key=True)
	email = db.Column(db.String(128), unique=True, index=True)
	username = db.Column(db.String(128), unique=True, index=True)
	password_hash = db.Column(db.String(128))

	def set_password(self, password):
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

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

