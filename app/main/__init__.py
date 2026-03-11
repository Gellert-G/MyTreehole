from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models import Post, Like, Favorite, Comment
from app.forms import PostForm, CommentForm, SearchForm
import random

bp = Blueprint('main', __name__)


def generate_anonymous_name(post_id):
    adjectives = ['快乐的', '悲伤的', '神秘的', '勇敢的', '温柔的', '聪明的', '安静的', '活泼的']
    nouns = ['小猫', '小狗', '小鸟', '小鱼', '小兔', '小熊', '小狐狸', '小鹿']
    random.seed(post_id)
    return random.choice(adjectives) + random.choice(nouns)


@bp.route('/', methods=['GET', 'POST'])
def index():
    form = PostForm()
    search_form = SearchForm()
    page = request.args.get('page', 1, type=int)
    
    if form.validate_on_submit() and current_user.is_authenticated:
        post = Post(content=form.content.data, user_id=current_user.id)
        db.session.add(post)
        db.session.commit()
        flash('发布成功！')
        return redirect(url_for('main.index'))
    
    posts = Post.query.order_by(Post.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False)
    
    for post in posts.items:
        if not hasattr(post, 'anonymous_name'):
            post.anonymous_name = generate_anonymous_name(post.id)
    
    return render_template('index.html', title='我的树洞', form=form, posts=posts, search_form=search_form)


@bp.route('/post/<int:post_id>/like', methods=['POST'])
@login_required
def like_post(post_id):
    post = Post.query.get_or_404(post_id)
    like = Like.query.filter_by(user_id=current_user.id, post_id=post_id).first()
    
    if like:
        db.session.delete(like)
        post.likes = max(0, post.likes - 1)
        liked = False
    else:
        like = Like(user_id=current_user.id, post_id=post_id)
        db.session.add(like)
        post.likes += 1
        liked = True
    
    db.session.commit()
    return jsonify({'liked': liked, 'likes_count': post.likes})


@bp.route('/post/<int:post_id>/favorite', methods=['POST'])
@login_required
def favorite_post(post_id):
    post = Post.query.get_or_404(post_id)
    favorite = Favorite.query.filter_by(user_id=current_user.id, post_id=post_id).first()
    
    if favorite:
        db.session.delete(favorite)
        post.favorites = max(0, post.favorites - 1)
        favorited = False
    else:
        favorite = Favorite(user_id=current_user.id, post_id=post_id)
        db.session.add(favorite)
        post.favorites += 1
        favorited = True
    
    db.session.commit()
    return jsonify({'favorited': favorited, 'favorites_count': post.favorites})


@bp.route('/post/<int:post_id>/comment', methods=['POST'])
@login_required
def comment_post(post_id):
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(content=form.content.data, user_id=current_user.id, post_id=post_id)
        db.session.add(comment)
        db.session.commit()
        flash('评论成功！')
    return redirect(url_for('main.index'))


@bp.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.user_id != current_user.id:
        flash('您没有权限删除此言论')
        return redirect(url_for('main.index'))
    
    db.session.delete(post)
    db.session.commit()
    flash('言论已删除')
    return redirect(url_for('main.index'))


@bp.route('/search')
def search():
    search_form = SearchForm()
    q = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    
    if q:
        posts = Post.query.filter(Post.content.contains(q)).order_by(Post.created_at.desc()).paginate(
            page=page, per_page=10, error_out=False)
    else:
        posts = None
    
    for post in posts.items if posts else []:
        if not hasattr(post, 'anonymous_name'):
            post.anonymous_name = generate_anonymous_name(post.id)
    
    return render_template('search.html', title='搜索结果', search_form=search_form, posts=posts, q=q)
