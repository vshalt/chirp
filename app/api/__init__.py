from flask import Blueprint

api_blueprint = Blueprint('api', __name__)

from app.api import authentication, comments, decorators, errors, posts, users
