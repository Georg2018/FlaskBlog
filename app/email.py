from flask import current_app, render_template
from flask_mail import Message
from . import mail
from threading import Thread

def async_sender(app, msg):
	with app.app_context():
		mail.send(msg)

def send_mail(to, subject, template, **kwargs):
	app = current_app._get_current_object()
	msg = Message(app.config['MAIL_SUBJECT_PREFIX']+' '+subject, sender=app.config['MAIL_DEFAULT_SENDER'], recipients=[to])
	msg.body = render_template(template+'.txt', **kwargs)
	msg.html = render_template(template+'.html', **kwargs)
	thr = Thread(target=async_sender, args=[app, msg])
	thr.start()
	return thr