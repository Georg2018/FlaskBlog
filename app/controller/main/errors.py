from flask import render_template
from . import main


@main.app_errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404


@main.app_errorhandler(403)
def permission_denied(error):
    return render_template("403.html"), 403


@main.app_errorhandler(500)
def server_error(error):
    return render_template("500.html"), 500
