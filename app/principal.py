from flask_principal import Permission, Need
from functools import partial

need = partial(Need, 'permission')

def require(name):
	permission = Permission(Need('permission', name))
	return permission.require(403)