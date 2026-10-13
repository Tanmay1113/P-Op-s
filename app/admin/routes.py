from flask import render_template, request, redirect, url_for, flash, abort
from sqlalchemy import or_
from ..extensions import db
from ..models import User, ROLES
from ..permissions import roles_required
from . import bp

@bp.get("/users")
@roles_required("Admin")
def users():
    query = request.args.get("q", "").strip()
    stmt = User.query
    if query:
        stmt = stmt.filter(or_(User.username.ilike(f"%{query}%"), User.email.ilike(f"%{query}%")))
    users = stmt.order_by(User.created_at.desc()).paginate(page=request.args.get("page", 1, type=int), per_page=20, error_out=False)
    return render_template("users/list.html", users=users, q=query)

@bp.route("/users/new", methods=["GET", "POST"])
@roles_required("Admin")
def create_user():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        role = request.form.get("role", "Employee")
        password = request.form.get("password", "")
        if len(username) < 3 or len(username) > 80:
            flash("Username must be between 3 and 80 characters.", "error")
        elif "@" not in email or len(email) > 254:
            flash("Enter a valid email address.", "error")
        elif role not in ROLES:
            flash("Select a valid role.", "error")
        elif len(password) < 12:
            flash("Password must contain at least 12 characters.", "error")
        elif User.query.filter(or_(User.username == username, User.email == email)).first():
            flash("That username or email is already in use.", "error")
        else:
            user = User(username=username, email=email, role=role)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash("User account created.", "success")
            return redirect(url_for("admin.users"))
    return render_template("users/form.html", roles=ROLES, user=None)

@bp.route("/users/<int:user_id>/edit", methods=["GET", "POST"])
@roles_required("Admin")
def edit_user(user_id):
    user = db.session.get(User, user_id) or abort(404)
    if request.method == "POST":
        role = request.form.get("role")
        active = request.form.get("active") == "yes"
        if role not in ROLES:
            flash("Select a valid role.", "error")
        elif user.user_id == __import__("flask_login").current_user.user_id and (role != "Admin" or not active):
            flash("You cannot remove your own active Admin access.", "error")
        elif user.role == "Admin" and user.is_active_account and (role != "Admin" or not active) and User.query.filter_by(role="Admin", is_active_account=True).count() <= 1:
            flash("At least one active Admin must remain.", "error")
        else:
            user.role = role
            user.is_active_account = active
            db.session.commit()
            flash("User updated.", "success")
            return redirect(url_for("admin.users"))
    return render_template("users/form.html", roles=ROLES, user=user)
