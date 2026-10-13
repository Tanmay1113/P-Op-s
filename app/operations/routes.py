from flask import render_template, request, redirect, url_for, flash, abort
from flask_login import current_user
from ..extensions import db
from ..models import Project, Operation, OPERATION_STATUSES
from ..permissions import roles_required
from . import bp

def scoped_projects():
    query = Project.query
    if current_user.role == "Manager":
        query = query.filter_by(created_by=current_user.user_id)
    return query

@bp.get("/")
@roles_required("Admin", "Manager")
def list_operations():
    project_ids = [p.project_id for p in scoped_projects().all()]
    query = Operation.query.filter(Operation.project_id.in_(project_ids)) if project_ids else Operation.query.filter(db.false())
    records = query.order_by(Operation.timestamp.desc()).paginate(page=request.args.get("page", 1, type=int), per_page=20, error_out=False)
    return render_template("operations/list.html", records=records)

@bp.route("/new", methods=["GET", "POST"])
@roles_required("Manager")
def create_operation():
    projects = scoped_projects().order_by(Project.name).all()
    if request.method == "POST":
        try:
            project_id = int(request.form.get("project_id", ""))
        except ValueError:
            project_id = -1
        project = Project.query.filter_by(project_id=project_id, created_by=current_user.user_id).first()
        kind = request.form.get("type", "").strip()
        status = request.form.get("status", "Open")
        if not project:
            flash("Choose a project you manage.", "error")
        elif not kind or len(kind) > 180:
            flash("Operation description is required and must be at most 180 characters.", "error")
        elif status not in OPERATION_STATUSES:
            flash("Choose a valid operation status.", "error")
        else:
            record = Operation(project_id=project.project_id, type=kind, status=status, logged_by=current_user.user_id)
            db.session.add(record)
            db.session.commit()
            flash("Operation logged.", "success")
            return redirect(url_for("operations.list_operations"))
    return render_template("operations/form.html", projects=projects, statuses=OPERATION_STATUSES)

@bp.post("/<int:operation_id>/status")
@roles_required("Manager")
def update_status(operation_id):
    record = db.session.get(Operation, operation_id) or abort(404)
    project = Project.query.filter_by(project_id=record.project_id, created_by=current_user.user_id).first()
    if not project:
        abort(403)
    status = request.form.get("status")
    if status not in OPERATION_STATUSES:
        flash("Choose a valid status.", "error")
    else:
        record.status = status
        db.session.commit()
        flash("Operation updated.", "success")
    return redirect(url_for("operations.list_operations"))
