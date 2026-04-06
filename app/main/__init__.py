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
        # 发帖用户固定显示为"洞主"
        post.anonymous_name = "洞主"
        
        # 获取所有评论，按时间顺序排序（最早的评论在前）
        comments = Comment.query.filter_by(post_id=post.id).order_by(Comment.created_at.asc()).all()
        
        # 为每个用户分配固定的匿名昵称
        user_nicknames = {}
        # 首先添加发帖用户
        user_nicknames[post.user_id] = "洞主"
        
        # 为评论用户分配昵称，从"A"开始
        next_letter = ord('A')
        for comment in comments:
            if comment.user_id not in user_nicknames:
                user_nicknames[comment.user_id] = chr(next_letter)
                next_letter += 1
            # 为评论设置匿名昵称
            comment.anonymous_name = user_nicknames[comment.user_id]
        
        # 由于post.comments是一个动态查询对象，我们需要将评论列表存储在一个新的属性中
        post.comment_list = comments
    
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
    content = request.form.get('content')
    if content:
        comment = Comment(content=content, user_id=current_user.id, post_id=post_id)
        db.session.add(comment)
        db.session.commit()
        
        # 为新评论生成匿名昵称
        post = Post.query.get_or_404(post_id)
        # 获取所有评论，按时间顺序排序（最早的评论在前）
        comments = Comment.query.filter_by(post_id=post_id).order_by(Comment.created_at.asc()).all()
        # 为每个用户分配固定的匿名昵称
        user_nicknames = {}
        # 首先添加发帖用户
        user_nicknames[post.user_id] = "洞主"
        # 为评论用户分配昵称，从"A"开始
        next_letter = ord('A')
        for c in comments:
            if c.user_id not in user_nicknames:
                user_nicknames[c.user_id] = chr(next_letter)
                next_letter += 1
        
        # 构造评论响应数据
        comment_data = {
            'id': comment.id,
            'content': comment.content,
            'anonymous_name': user_nicknames[comment.user_id],
            'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M')
        }
        
        # 检查请求是否来自AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or 'application/json' in request.headers.get('Accept', ''):
            return jsonify({'success': True, 'comment': comment_data})
        else:
            # 对于非AJAX请求，重定向回原页面
            flash('评论成功！')
            return redirect(request.referrer or url_for('main.index'))
    
    # 检查请求是否来自AJAX
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or 'application/json' in request.headers.get('Accept', ''):
        return jsonify({'success': False, 'message': '评论内容不能为空'})
    else:
        # 对于非AJAX请求，重定向回原页面
        flash('评论内容不能为空')
        return redirect(request.referrer or url_for('main.index'))


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
        # 发帖用户固定显示为"洞主"
        post.anonymous_name = "洞主"
        
        # 获取所有评论，按时间顺序排序（最早的评论在前）
        comments = Comment.query.filter_by(post_id=post.id).order_by(Comment.created_at.asc()).all()
        
        # 为每个用户分配固定的匿名昵称
        user_nicknames = {}
        # 首先添加发帖用户
        user_nicknames[post.user_id] = "洞主"
        
        # 为评论用户分配昵称，从"A"开始
        next_letter = ord('A')
        for comment in comments:
            if comment.user_id not in user_nicknames:
                user_nicknames[comment.user_id] = chr(next_letter)
                next_letter += 1
            # 为评论设置匿名昵称
            comment.anonymous_name = user_nicknames[comment.user_id]
        
        # 由于post.comments是一个动态查询对象，我们需要将评论列表存储在一个新的属性中
        post.comment_list = comments
    
    return render_template('search.html', title='搜索结果', search_form=search_form, posts=posts, q=q)


@bp.route('/post/<int:post_id>')
def view_post(post_id):
    post = Post.query.get_or_404(post_id)
    # 发帖用户固定显示为"洞主"
    post.anonymous_name = "洞主"
    
    form = PostForm()
    search_form = SearchForm()
    comment_form = CommentForm()
    
    # 获取所有评论，按时间顺序排序（最早的评论在前）
    comments = Comment.query.filter_by(post_id=post_id).order_by(Comment.created_at.asc()).all()
    
    # 为每个用户分配固定的匿名昵称
    user_nicknames = {}
    # 首先添加发帖用户
    user_nicknames[post.user_id] = "洞主"
    
    # 为评论用户分配昵称，从"A"开始
    next_letter = ord('A')
    for comment in comments:
        if comment.user_id not in user_nicknames:
            user_nicknames[comment.user_id] = chr(next_letter)
            next_letter += 1
        # 为评论设置匿名昵称
        comment.anonymous_name = user_nicknames[comment.user_id]
    
    # 重新按时间顺序排序（最新的评论在前）
    comments.reverse()
    
    return render_template('post.html', title='言论详情', post=post, form=form, 
                          search_form=search_form, comment_form=comment_form, comments=comments)


@bp.route('/post/<int:post_id>/comments')
def get_comments(post_id):
    # 获取排序方式，默认逆序
    sort = request.args.get('sort', 'desc')
    
    post = Post.query.get_or_404(post_id)
    
    # 获取所有评论，按时间顺序排序
    if sort == 'asc':
        comments = Comment.query.filter_by(post_id=post_id).order_by(Comment.created_at.asc()).all()
    else:
        comments = Comment.query.filter_by(post_id=post_id).order_by(Comment.created_at.desc()).all()
    
    # 为每个用户分配固定的匿名昵称
    user_nicknames = {}
    # 首先添加发帖用户
    user_nicknames[post.user_id] = "洞主"
    
    # 为评论用户分配昵称，从"A"开始
    next_letter = ord('A')
    # 按时间顺序遍历评论，确保昵称分配一致
    all_comments = Comment.query.filter_by(post_id=post_id).order_by(Comment.created_at.asc()).all()
    for comment in all_comments:
        if comment.user_id not in user_nicknames:
            user_nicknames[comment.user_id] = chr(next_letter)
            next_letter += 1
    
    # 构造评论响应数据
    comments_data = []
    for comment in comments:
        comments_data.append({
            'id': comment.id,
            'content': comment.content,
            'anonymous_name': user_nicknames[comment.user_id],
            'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M')
        })
    
    return jsonify({'comments': comments_data})
