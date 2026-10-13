
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
@limiter.limit("5 per minute", methods=["POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not username or not email or not password:
            flash("Please fill in all required fields.", "error")
            return render_template("auth/register.html")

        if len(username) > 80:
            flash("Username must be 80 characters or fewer.", "error")
            return render_template("auth/register.html")

        if len(email) > 254 or "@" not in email:
            flash("Please enter a valid email address.", "error")
            return render_template("auth/register.html")

        if len(password) < 12:
            flash("Password must be at least 12 characters long.", "error")
            return render_template("auth/register.html")

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return render_template("auth/register.html")

        existing_user = User.query.filter(
            or_(
                User.username == username,
                User.email == email
            )
        ).first()

        if existing_user:
            flash("That username or email is already registered.", "error")
            return render_template("auth/register.html")

        user = User(
            username=username,
            email=email,
            role="Employee",
            is_active_account=True
        )
        user.set_password(password)

        try:
            db.session.add(user)
            db.session.commit()
        except Exception:
            db.session.rollback()
            flash("Account creation failed. Please try again.", "error")
            return render_template("auth/register.html")

        flash("Account created successfully. You can now sign in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")


@bp.post("/logout")
def logout():
    if current_user.is_authenticated:
        logout_user()

    flash("You have been signed out.", "success")
    return redirect(url_for("home"))
