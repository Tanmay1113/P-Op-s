from datetime import datetime, timezone
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .extensions import db, login_manager

ROLES = ("Admin", "Manager", "Employee")
PROJECT_STATUSES = ("Active", "Completed", "On-hold")
TASK_STATUSES = ("Pending", "In Progress", "Completed")
OPERATION_STATUSES = ("Open", "Closed")

def utcnow():
    return datetime.now(timezone.utc)

class User(UserMixin, db.Model):
    __tablename__ = "users"
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(254), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="Employee")
    is_active_account = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)

    created_projects = db.relationship("Project", back_populates="creator", foreign_keys="Project.created_by")
    assigned_tasks = db.relationship("Task", back_populates="assignee", foreign_keys="Task.assigned_to")
    logged_operations = db.relationship("Operation", back_populates="logger", foreign_keys="Operation.logged_by")

    def get_id(self):
        return str(self.user_id)

    @property
    def is_active(self):
        return self.is_active_account

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method="scrypt")

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    try:
        return db.session.get(User, int(user_id))
    except (TypeError, ValueError):
        return None

class Project(db.Model):
    __tablename__ = "projects"
    project_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(160), nullable=False)
    description = db.Column(db.Text, nullable=False, default="")
    status = db.Column(db.String(20), nullable=False, default="Active")
    created_by = db.Column(db.Integer, db.ForeignKey("users.user_id", ondelete="RESTRICT"), nullable=False, index=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)

    creator = db.relationship("User", back_populates="created_projects", foreign_keys=[created_by])
    tasks = db.relationship("Task", back_populates="project", cascade="all, delete-orphan")
    operations = db.relationship("Operation", back_populates="project", cascade="all, delete-orphan")

class Task(db.Model):
    __tablename__ = "tasks"
    task_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(180), nullable=False)
    description = db.Column(db.Text, nullable=False, default="")
    project_id = db.Column(db.Integer, db.ForeignKey("projects.project_id", ondelete="CASCADE"), nullable=False, index=True)
    assigned_to = db.Column(db.Integer, db.ForeignKey("users.user_id", ondelete="RESTRICT"), nullable=False, index=True)
    status = db.Column(db.String(20), nullable=False, default="Pending")
    deadline = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)

    project = db.relationship("Project", back_populates="tasks")
    assignee = db.relationship("User", back_populates="assigned_tasks", foreign_keys=[assigned_to])

class Operation(db.Model):
    __tablename__ = "operations"
    operation_id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.project_id", ondelete="CASCADE"), nullable=False, index=True)
    type = db.Column(db.String(180), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="Open")
    logged_by = db.Column(db.Integer, db.ForeignKey("users.user_id", ondelete="RESTRICT"), nullable=False, index=True)
    timestamp = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)

    project = db.relationship("Project", back_populates="operations")
    logger = db.relationship("User", back_populates="logged_operations", foreign_keys=[logged_by])
