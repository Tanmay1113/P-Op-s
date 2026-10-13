from flask import Blueprint

bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")

from . import routes as routes  # noqa: E402