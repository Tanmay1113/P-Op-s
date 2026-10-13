
from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user, login_user, logout_user
from sqlalchemy import or_
from ..extensions import db, limiter
from ..models import User
from . import bp


@bp.route("/login", methods=["GET", "POST"])
@limiter.limit("10 per minute", methods=["POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        identity = request.form.get("identity", "").strip()
        password = request.form.get("password", "")

        user = User.query.filter(
            or_(
                User.username == identity,
                User.email == identity.lower()
            )
        ).first()

        if (
            user
            and user.is_active_account
            and user.check_password(password)
        ):
            login_user(user, remember=False, fresh=True)

            from flask import session
            session.permanent = True

            flash("Welcome back.", "success")
            return redirect(url_for("dashboard.index"))

        flash("Unable to sign in with those details.", "error")

    return render_template("auth/login.html")


@bp.route("/register", methods=["GET", "POST"])
def register():
    return (
        "Public registration is disabled. Contact your system administrator.",
        403,
    )


@bp.post("/logout")
def logout():
    if current_user.is_authenticated:
        logout_user()

    flash("You have been signed out.", "success")
    return redirect(url_for("home"))
