from app.api import api_blueprint
from app.models import Comment
from flask import request, url_for, current_app, jsonify

@api_blueprint.route('/comments/')
def get_comments():
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(page=page, per_page=current_app.config['COMMENTS_PER_PAGE'], error_out=False)
    comments = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_comments', id=id, page=page-1)
    next = None
    if pagination.has_next:
        next = url_for('api.get_comments', id=id, page=page+1)
    return jsonify({
        'comments': [comment.to_json() for comment in comments],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })

@api_blueprint.route('/comments/<int:id>')
def get_comment(id):
    comment = Comment.query.get_or_404(id)
    return jsonify(comment.to_json())
