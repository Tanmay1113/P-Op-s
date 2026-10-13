from flask import render_template, request, redirect, url_for, flash, abort
from flask_login import current_user
from ..extensions import db
from ..models import Project, PROJECT_STATUSES
from ..permissions import roles_required
from . import bp

def get_project(project_id):
    project = db.session.get(Project, project_id) or abort(404)
    if current_user.role == "Manager" and project.created_by != current_user.user_id:
        abort(403)
    if current_user.role not in ("Admin", "Manager"):
        abort(403)
    return project

@bp.get("/")
@roles_required("Admin", "Manager")
def list_projects():
    query = Project.query
    if current_user.role == "Manager":
        query = query.filter_by(created_by=current_user.user_id)
    projects = query.order_by(Project.created_at.desc()).paginate(page=request.args.get("page", 1, type=int), per_page=20, error_out=False)
    return render_template("projects/list.html", projects=projects)

@bp.route("/new", methods=["GET", "POST"])
@roles_required("Manager")
def create_project():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        status = request.form.get("status", "Active")
        if not name or len(name) > 160:
            flash("Project name is required and must be at most 160 characters.", "error")
        elif status not in PROJECT_STATUSES:
            flash("Select a valid project status.", "error")
        else:
            project = Project(name=name, description=description, status=status, created_by=current_user.user_id)
            db.session.add(project)
            db.session.commit()
            flash("Project created.", "success")
            return redirect(url_for("projects.detail", project_id=project.project_id))
    return render_template("projects/form.html", project=None, statuses=PROJECT_STATUSES)

@bp.get("/<int:project_id>")
@roles_required("Admin", "Manager")
def detail(project_id):
    project = get_project(project_id)
    return render_template("projects/detail.html", project=project)

@bp.route("/<int:project_id>/edit", methods=["GET", "POST"])
@roles_required("Manager")
def edit_project(project_id):
    project = get_project(project_id)
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        status = request.form.get("status", "Active")
        if not name or len(name) > 160:
            flash("Project name is required and must be at most 160 characters.", "error")
        elif status not in PROJECT_STATUSES:
            flash("Select a valid status.", "error")
        else:
            project.name = name
            project.description = request.form.get("description", "").strip()
            project.status = status
            db.session.commit()
            flash("Project updated.", "success")
            return redirect(url_for("projects.detail", project_id=project.project_id))
    return render_template("projects/form.html", project=project, statuses=PROJECT_STATUSES)
