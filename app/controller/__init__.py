"""
The controller of the application. Which include the logic of the interaction of each part of the application.
"""
from ..models import *
from ..extensions import send_mail, require, need

from .main import main
from .auth import auth
from .api import api_bp
