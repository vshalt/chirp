from app.main import main_blueprint
from flask import render_template


@main_blueprint.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@main_blueprint.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@main_blueprint.errorhandler(403)
def forbidden_page(e):
    return render_template('403.html'), 403
