from flask import Blueprint

bp = Blueprint("api", __name__)

from routes import auth  # noqa: E402, F401
from routes import shop  # noqa: E402, F401
