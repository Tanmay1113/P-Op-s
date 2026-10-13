from flask import Blueprint
bp = Blueprint("tasks", __name__, url_prefix="/tasks")
from . import routes
