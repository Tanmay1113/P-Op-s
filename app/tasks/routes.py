from datetime import date
from flask import render_template, request, redirect, url_for, flash, abort
from flask_login import current_user, login_required
from ..extensions import db
from ..models import Project, Task, User, TASK_STATUSES
from ..permissions import roles_required
from . import bp

def manager_project(project_id):
    project = db.session.get(Project, project_id) or abort(404)
    if current_user.role == "Manager" and project.created_by != current_user.user_id:
        abort(403)
    if current_user.role not in ("Manager", "Admin"):
        abort(403)
    return project

@bp.get("/")
@login_required
def list_tasks():
    if current_user.role == "Employee":
        query = Task.query.filter_by(assigned_to=current_user.user_id)
    elif current_user.role == "Manager":
        ids = [p.project_id for p in Project.query.filter_by(created_by=current_user.user_id).all()]
        query = Task.query.filter(Task.project_id.in_(ids)) if ids else Task.query.filter(db.false())
    else:
        query = Task.query
    tasks = query.order_by(Task.deadline.asc().nullslast()).paginate(page=request.args.get("page", 1, type=int), per_page=20, error_out=False)
    return render_template("tasks/list.html", tasks=tasks)

@bp.route("/new", methods=["GET", "POST"])
@roles_required("Manager")
def create_task():
    projects = Project.query.filter_by(created_by=current_user.user_id).order_by(Project.name).all()
    employees = User.query.filter_by(role="Employee", is_active_account=True).order_by(User.username).all()
    if request.method == "POST":
        try:
            project_id = int(request.form.get("project_id", ""))
            assigned_to = int(request.form.get("assigned_to", ""))
        except ValueError:
            flash("Choose a valid project and employee.", "error")
            return render_template("tasks/form.html", task=None, projects=projects, employees=employees, statuses=TASK_STATUSES)
        project = Project.query.filter_by(project_id=project_id, created_by=current_user.user_id).first()
        employee = User.query.filter_by(user_id=assigned_to, role="Employee", is_active_account=True).first()
        title = request.form.get("title", "").strip()
        status = request.form.get("status", "Pending")
        raw_deadline = request.form.get("deadline", "").strip()
        try:
            deadline = date.fromisoformat(raw_deadline) if raw_deadline else None
        except ValueError:
            deadline = None
            raw_deadline = "invalid"
        if not project or not employee:
            flash("Choose a project you manage and an active Employee.", "error")
        elif not title or len(title) > 180:
            flash("Task title is required and must be at most 180 characters.", "error")
        elif status not in TASK_STATUSES:
            flash("Choose a valid task status.", "error")
        elif raw_deadline == "invalid":
            flash("Enter a valid deadline.", "error")
        else:
            task = Task(title=title, description=request.form.get("description", "").strip(), project_id=project.project_id, assigned_to=employee.user_id, status=status, deadline=deadline)
            db.session.add(task)
            db.session.commit()
            flash("Task created and assigned.", "success")
            return redirect(url_for("tasks.list_tasks"))
    return render_template("tasks/form.html", task=None, projects=projects, employees=employees, statuses=TASK_STATUSES)

@bp.route("/<int:task_id>/status", methods=["POST"])
@roles_required("Employee", "Manager")
def update_status(task_id):
    task = db.session.get(Task, task_id) or abort(404)
    if current_user.role == "Employee":
        if task.assigned_to != current_user.user_id:
            abort(403)
    else:
        project = manager_project(task.project_id)
    status = request.form.get("status")
    if status not in TASK_STATUSES:
        flash("Choose a valid task status.", "error")
    else:
        task.status = status
        db.session.commit()
        flash("Task status updated.", "success")
    return redirect(request.referrer or url_for("tasks.list_tasks"))
