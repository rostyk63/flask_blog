from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user

from .models import Post, User, Comment, Like
from website import db

views = Blueprint('views', __name__)


@views.route('/')
@views.route('/home')
@login_required
def home():
    all_posts = Post.query.all()
    all_comments = Comment.query.all()
    return render_template('home.html', user=current_user, posts=all_posts, comments=all_comments)


@views.route('/create-post', methods=['GET', 'POST'])
@login_required
def create_post():
    if request.method == 'POST':
        text = request.form.get('text')
        if not text:
            flash('Post cannot be empty.', category='error')
        else:
            post = Post(text=text, author=current_user.id)
            db.session.add(post)
            db.session.commit()
            flash('Post created!', category='success')
            return redirect(url_for('views.home'))
    return render_template('create_post.html', user=current_user)


@views.route('/delete-post/<int:post_id>')
@login_required
def delete_post(post_id):
    post = Post.query.filter_by(id=post_id).first()
    if not post:
        flash('Post does not exist.', category='error')
    elif current_user.id != post.author:
        flash('You have no permission to delete this post.', category='error')
    else:
        db.session.delete(post)
        db.session.commit()
        flash('Post deleted.', category='success')
    return redirect(url_for('views.home'))


@views.route('/posts/<user_name>')
@login_required
def posts(user_name):
    user = User.query.filter_by(user_name=user_name).first()
    if not user:
        flash('No user with that username exists.', category='error')
        return redirect(url_for('views.home'))
    user_posts = user.posts
    return render_template('posts.html', user=current_user, posts=user_posts, user_name=user_name)


@views.route('/create-comment/<post_id>', methods=['POST'])
@login_required
def create_comment(post_id):
    post = Post.query.get(post_id)
    if not post:
        flash('Post does not exist.', category='error')
    else:
        text = request.form.get('text')
        if not text:
            flash('Comment can not be empty.', category='error')
        else:
            comment = Comment(text=text, author=current_user.id, post_id=post.id)
            db.session.add(comment)
            db.session.commit()
            flash('Comment added.', category='success')
    return redirect(url_for('views.home', post=post))


@views.route('/delete-comment/<int:comment_id>')
@login_required
def delete_comment(comment_id):
    comment = Comment.query.filter_by(id=comment_id).first()
    if not comment.post_id:
        flash('Post does not exist.', category='error')
    elif not comment:
        flash('Comment does not exist.', category='error')
    elif current_user.id != comment.author and current_user.id != comment.post.author:
        flash('You have no permission to delete this comment.', category='error')
    else:
        db.session.delete(comment)
        db.session.commit()
        flash('Comment deleted.', category='success')
    return redirect(url_for('views.home'))


@views.route('/like-post/<post_id>', methods=['GET'])
@login_required
def like_manage(post_id):
    post = Post.query.get(post_id)
    like = Like.query.filter_by(author=current_user.id, post_id=post_id).first()
    if not post:
        flash('Post does not exist.', category='error')
    elif like:
        db.session.delete(like)
        db.session.commit()
    else:
        like = Like(author=current_user.id, post_id=post_id)
        db.session.add(like)
        db.session.commit()
    return redirect(url_for('views.home'))
