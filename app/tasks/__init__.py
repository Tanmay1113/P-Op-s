from flask import Blueprint

bp = Blueprint("tasks", __name__, url_prefix="/tasks")

from . import routes as routes  # noqa: E402