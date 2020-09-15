from app.main import main_blueprint
from flask import render_template, request, jsonify


@main_blueprint.errorhandler(404)
def page_not_found(e):
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'not found'})
        response.status_code = 404
        return response
    return render_template('404.html'), 404


@main_blueprint.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@main_blueprint.errorhandler(403)
def forbidden_page(e):
    return render_template('403.html'), 403
