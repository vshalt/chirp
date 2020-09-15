from app.api import api_blueprint
from flask import request, jsonify, g, url_for, current_app
from app.models import Post, Comment
from app import db
from app.api.decorators import permission_required
from app.models import Permission
from app.api.errors import forbidden

@api_blueprint.route('/posts/', methods=['POST'])
@permission_required(Permission.WRITE)
def new_post():
    post = Post.from_json(request.json)
    post.author = g.current_user
    db.session.add(post)
    db.session.commit()
    return jsonify(post.to_json()), 201, {'Location': url_for('api.get_post', id = post.id)}

@api_blueprint.route('/posts/')
def get_posts():
    posts = Post.query.all()
    return jsonify({'posts': [post.to_json() for post in posts]})

@api_blueprint.route('/posts/<int:id>')
def get_post(id):
    post = Post.query.get_or_404(id)
    return jsonify({post.to_json()})

@api_blueprint.route('/posts/<int:id>', methods=['PUT'])
@permission_required(Permission.WRITE)
def edit_post(id):
    post = Post.query.get_or_404(id)
    if g.current_user != post.author or g.current_user.can(Permission.ADMIN):
        return forbidden('Insufficient permissions')
    post.body = request.json.get('body', post.body)
    db.session.add(post)
    db.session.commit()
    return jsonify(post.to_json())

@api_blueprint.route('/posts/<int:id>/comments')
def get_post_comment(id):
    post = Post.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    pagination = post.comments.order_by(Comment.timestamp.desc()).paginate(page=page, per_page = current_app.config['COMMENTS_PER_PAGE'], error_out = False)
    comments = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_post_comment', id=id, page=page-1)
    next = None
    if pagination.has_next:
        next = url_for('api.get_post_comment', id=id, page=page+1)
    return jsonify({
        'comments': [comment.to_json() for comment in comments],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })

@api_blueprint.route('/posts/<int:id>/comments')
@permission_required(Permission.COMMENT)
def new_post_comment(id):
    post = Post.query.get_or_404(id)
    comment = Comment.from_json(request.json)
    comment.author = g.current_user
    comment.post = post
    db.session.add(comment)
    db.session.commit()
    return jsonify(comment.to_json()), 201, {'location': url_for('api.get_comment', id=comment.id)}
