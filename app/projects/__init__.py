from flask import Blueprint
bp = Blueprint("projects", __name__, url_prefix="/projects")
from . import routes
