from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models import Post, Favorite
import random

bp = Blueprint('profile', __name__)


def generate_anonymous_name(post_id):
    adjectives = ['快乐的', '悲伤的', '神秘的', '勇敢的', '温柔的', '聪明的', '安静的', '活泼的']
    nouns = ['小猫', '小狗', '小鸟', '小鱼', '小兔', '小熊', '小狐狸', '小鹿']
    random.seed(post_id)
    return random.choice(adjectives) + random.choice(nouns)


@bp.route('/')
@login_required
def index():
    posts_count = Post.query.filter_by(user_id=current_user.id).count()
    favorites_count = Favorite.query.filter_by(user_id=current_user.id).count()
    return render_template('profile/index.html', title='个人中心', 
                          posts_count=posts_count, favorites_count=favorites_count)


@bp.route('/posts')
@login_required
def posts():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(user_id=current_user.id).order_by(
        Post.created_at.desc()).paginate(page=page, per_page=10, error_out=False)
    
    for post in posts.items:
        if not hasattr(post, 'anonymous_name'):
            post.anonymous_name = generate_anonymous_name(post.id)
    
    return render_template('profile/posts.html', title='我的发表', posts=posts)


@bp.route('/favorites')
@login_required
def favorites():
    page = request.args.get('page', 1, type=int)
    favorites = Favorite.query.filter_by(user_id=current_user.id).order_by(
        Favorite.created_at.desc()).paginate(page=page, per_page=10, error_out=False)
    
    posts = [fav.post for fav in favorites.items]
    
    for post in posts:
        if not hasattr(post, 'anonymous_name'):
            post.anonymous_name = generate_anonymous_name(post.id)
    
    return render_template('profile/favorites.html', title='我的收藏', 
                          posts=posts, pagination=favorites)
