from flask import Blueprint

bp = Blueprint("operations", __name__, url_prefix="/operations")

from . import routes as routes  # noqa: E402
