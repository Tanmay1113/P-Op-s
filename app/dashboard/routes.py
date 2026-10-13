from flask import render_template
from flask_login import current_user, login_required
from ..extensions import db
from ..models import User, Project, Task, Operation
from . import bp

@bp.get("/")
@login_required
def index():
    if current_user.role == "Admin":
        stats = {
            "users": User.query.count(),
            "projects": Project.query.count(),
            "tasks": Task.query.count(),
            "operations": Operation.query.filter_by(status="Open").count(),
        }
        recent_projects = Project.query.order_by(Project.created_at.desc()).limit(5).all()
        return render_template("dashboard/admin.html", stats=stats, recent_projects=recent_projects)
    if current_user.role == "Manager":
        projects = Project.query.filter_by(created_by=current_user.user_id).order_by(Project.created_at.desc()).all()
        project_ids = [p.project_id for p in projects]
        task_query = Task.query.filter(Task.project_id.in_(project_ids)) if project_ids else Task.query.filter(db.false())
        stats = {
            "projects": len(projects),
            "tasks": task_query.count(),
            "pending": task_query.filter_by(status="Pending").count(),
            "operations": Operation.query.filter(Operation.project_id.in_(project_ids), Operation.status=="Open").count() if project_ids else 0,
        }
        upcoming = task_query.filter(Task.deadline.isnot(None), Task.status != "Completed").order_by(Task.deadline.asc()).limit(6).all()
        return render_template("dashboard/manager.html", stats=stats, projects=projects[:5], upcoming=upcoming)
    tasks = Task.query.filter_by(assigned_to=current_user.user_id).order_by(Task.deadline.asc().nullslast()).all()
    stats = {status: sum(1 for t in tasks if t.status == status) for status in ("Pending", "In Progress", "Completed")}
    return render_template("dashboard/employee.html", tasks=tasks[:10], stats=stats)
