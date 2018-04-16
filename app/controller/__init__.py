'''
The controller of the application. Which include the logic of the interaction of each part of the application.
'''
from ..models import *
from ..email import send_mail

from .main import main
from .auth import auth

