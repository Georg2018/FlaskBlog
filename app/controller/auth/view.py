"""
Auth blueprint's view. Defined the route of the auth blueprint and the related logic.
"""
import re
from flask import (
    render_template, url_for, redirect, flash, request, current_app, make_response
)
from flask_login import current_user, login_required, login_user, logout_user
from flask_principal import Identity, AnonymousIdentity, identity_changed, Permission
from .forms import (
    RegisterForm,
    LoginForm,
    ChangePasswordForm,
    ChangeMailForm,
    AuthResetPassForm,
    ResetPassForm,
)
from . import auth
from .. import db, User, send_mail, require, need


@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.update_last_since()
        db.session.add(current_user._get_current_object())
        db.session.commit()
        if (
            not current_user.confirmed
            and request.endpoint
            and request.blueprint != "auth"
            and request.endpoint != "static"
            and not Permission(need("admin")).can()
        ):
            return render_template("auth/unconfirmed.html")


@auth.route("register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            email=form.email.data,
            username=form.username.data,
            password=form.password.data,
        )

        db.session.add(user)
        db.session.commit()

        token = user.generate_confirmed_token()

        send_mail(
            user.email,
            "Confirmed your account.",
            "/auth/mail/confirmed",
            user=user,
            token=token,
        )

        flash("You have successfully registered a account.")
        flash(
            "We have send a confirmed email to your mailbox. Please check it for verification."
        )
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html", form=form)


@auth.route("login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = LoginForm()
    if form.validate_on_submit():
        if re.match("^[a-zA-Z0-9.]+@[a-zA-Z0-9]+\.[a-zA-Z]+$", form.identifier.data):
            user = User.query.filter_by(_email=form.identifier.data).first()
        else:
            user = User.query.filter_by(username=form.identifier.data).first()

        if user is not None and user.check_password(form.password.data):
            login_user(user, form.remember_me.data)
            identity_changed.send(
                current_app._get_current_object(), identity=Identity(user.id)
            )
            if Permission(need("admin")).can():
                flash("Hello, admin!")
            return redirect(request.args.get("next") or url_for("main.index"))

        else:
            flash("Your username/email or password is invalid.")
            return redirect(url_for("auth.login"))

    return render_template("auth/login.html", form=form)


@auth.route("logout")
def logout():
    if not current_user.is_authenticated:
        flash("You have not logined in.")
        return redirect(url_for("main.index"))

    logout_user()
    identity_changed.send(
        current_app._get_current_object(), identity=AnonymousIdentity()
    )
    resp = make_response(redirect(url_for("main.index")))
    resp.set_cookie("show_followed", "", 60 * 60 * 24 * 30)
    return resp


@auth.route("confirmed")
@auth.route("confirmed/<token>")
def confirmed(token=""):
    """
	Email confirmed.
	"""
    if current_user.is_authenticated and current_user.confirmed:
        flash("You have been confirmed.")
        return redirect(url_for("main.index"))

    user_id = User.verify_confirmed_token(token)

    if user_id:
        flash("You have successfully verify your account.")
        return redirect(url_for("auth.login"))

    flash("Some errors are happend.")
    return redirect(url_for("main.index"))


@auth.route("resendMail")
def resendMail():
    """
	Resend confirmed email.
	"""
    if current_user.confirmed:
        return redirect(url_for("main.index"))

    if not current_user.is_authenticated:
        return redirect(url_for("auth.login"))

    token = current_user.generate_confirmed_token()
    send_mail(
        current_user.email,
        "Confirmed your account.",
        "/auth/mail/confirmed",
        user=current_user,
        token=token,
    )

    flash("We have resent a confirmed email.")
    return render_template("auth/unconfirmed.html")


@auth.route("changepass", methods=["GET", "POST"])
@login_required
def changepass():
    """
	Change password, only when the user know the original password.
	"""
    form = ChangePasswordForm()
    if form.validate_on_submit():
        user = current_user._get_current_object()

        if user.check_password(form.old_password.data):
            user.password = form.new_password.data
            db.session.add(user)
            db.session.commit()

            logout()

            flash("You have successfully changed your password. Please login again.")
            return redirect(url_for("auth.login"))

        else:
            flash("Original password error. Please try again.")
            return redirect(url_for("auth.changepass"))

    return render_template("auth/changepass.html", form=form)


@auth.route("changemail", methods=["GET", "POST"])
@login_required
def changemail():
    """
	Change the email only when the user know his password.
	"""
    form = ChangeMailForm()
    if form.validate_on_submit():
        if current_user.check_password(form.password.data):
            user = current_user._get_current_object()
            user.email = form.new_email.data
            user.confirmed = False
            db.session.add(user)
            db.session.commit()

            token = user.generate_confirmed_token()
            send_mail(
                user.email,
                "Confirmed your email.",
                "/auth/mail/confirmed",
                user=user,
                token=token,
            )

            flash(
                "Please check the email that we sent to your new mailbox to update your account."
            )
            return redirect(url_for("main.index"))

        else:
            flash("Password error.")
            return redirect(url_for("auth.changemail"))

    return render_template("auth/changemail.html", form=form)


@auth.route("authresetpass", methods=["GET", "POST"])
def authresetpass():
    """
	Get the username of the user who forgets his password.
	"""
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = AuthResetPassForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user is None:
            flash("This username doesn't exist.")
            return redirect(url_for("auth.authresetpass"))

        token = user.generate_resetpass_token()
        send_mail(
            user.email,
            "Reset password.",
            "/auth/mail/resetpass",
            user=user,
            token=token,
        )

        flash("We have seet a mail to you. Please check the mail to reset password.")
        return redirect(url_for("auth.login"))

    return render_template("auth/authresetpass.html", form=form)


@auth.route("resetpass/<token>", methods=["GET", "POST"])
def resetpass(token=""):
    """
	Verify the token then reset the user's password.
	"""
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = ResetPassForm()
    if form.validate_on_submit():
        user = User.verify_resetpass_token(token)
        if user:
            user.password = form.password.data
            db.session.add(user)
            db.session.commit()

            flash("You have successfully resert your password. Please login again.")
            return redirect(url_for("auth.login"))

        else:
            return redirect(url_for("main.index"))

    form.token = token
    return render_template("/auth/resetpass.html", form=form)
