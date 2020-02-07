from .. import db
from flask import render_template, request, url_for, redirect, flash, Blueprint
from flask_login import login_required, current_user
from ..models import User, Posts
from ..userShop.views import current_role, role_req
import time
import logging

postShop = Blueprint('postShop', __name__, template_folder='templates')
logging.basicConfig(level=logging.INFO)


@postShop.route('/posts', methods=["GET"])
def posts():
    get_posts = db.session.query(Posts.title).all()
    get_posts = ([n[0] for n in get_posts])
    posts_list = []
    for post in get_posts:
        posts_list.append(post)
    if not posts_list:
        return render_template("posts.html")
    elif len(posts_list) == 1:
        page_post = posts_list[0]
    else:
        page_post = posts_list[len(posts_list) - 1]
    post_db = Posts.query.filter_by(title=page_post).first()
    post = Posts.query.filter_by(id=post_db.id).first().post
    title = Posts.query.filter_by(id=post_db.id).first().title
    user = Posts.query.filter_by(id=post_db.id).first().user
    time_date = Posts.query.filter_by(id=post_db.id).first().time_date
    post_id = Posts.query.filter_by(id=post_db.id).first().id
    posts_list2 = []
    number_of_visible_posts = 4
    i = 0
    if len(posts_list) == 0 or len(posts_list) == 1:
        return render_template("posts.html", title=title, post=post, user=user, post_id=post_id, time=time_date)
    elif len(posts_list) == 2:
        page_post2 = posts_list[0]
        post2 = Posts.query.filter_by(title=page_post2).first()
        posts_list2.append(post2)
    else:
        while i != number_of_visible_posts:
            i += 1
            page_post2 = posts_list[len(posts_list) - (i+1)]
            post2 = Posts.query.filter_by(title=page_post2).first()
            posts_list2.append(post2)
    return render_template("posts.html", title=title, post=post, user=user, time=time_date,
                           post_id=post_id, posts_list2=posts_list2)


@postShop.route('/add_post', methods=['POST'])
def add_post():
    title_list = db.session.query(Posts.title).all()
    title_list = ([x[0] for x in title_list])
    title = request.form['title']
    if not title:
        flash("You have to add title", 'error')
        return redirect(url_for('shop.postShop'))
    elif title in title_list:
        flash("Post with the same title does exist", 'error')
        return redirect(url_for('shop.postShop'))
    post = request.form['post']
    if not post:
        flash("You have to add some text", 'error')
        return redirect(url_for('shop.postShop'))
    if current_user.is_anonymous:
        user = "Guest"
    else:
        user = current_user.username
    seconds = time.time()
    time_date = time.ctime(seconds)
    new_post = Posts(title=title, post=post, user=user, time=seconds, time_date=time_date)
    db.session.add(new_post)
    db.session.commit()
    return redirect(url_for('postShop.posts'))


@postShop.route('/remove_post', methods=['GET', 'POST'])
@login_required
def remove_post():
    rem_post = request.form.getlist("remove_post")  # post.id
    user = User.query.filter_by(username=current_user.username).first().username
    post_user_list = []
    post_user_filtered_list = []
    if 'all_posts_remove' in rem_post:
        pass
    else:
        for item in rem_post:
            post_user = Posts.query.filter_by(id=item).first().user
            post_user_list.append(post_user)
    if current_role() == role_req('admin'):
        if request.method == "POST":
            if 'all_posts_remove' in rem_post:
                Posts.query.filter().delete()
                db.session.commit()
            else:
                logging.info("Posts to remove %s", rem_post)
                for item in rem_post:
                    Posts.query.filter_by(id=item).delete()
                    db.session.commit()
                flash(f'Post: {rem_post} has been removed', 'success')
            return redirect(url_for('postShop.posts'))
    elif user in post_user_list:
        for item in rem_post:
            post_user = Posts.query.filter_by(id=item).first().user
            logging.info("User post %s", post_user)
            if post_user == user:
                post_user_filtered_list.append(item)
        logging.info("Post user filtered list%s", post_user_filtered_list)
        for item in post_user_filtered_list:
            Posts.query.filter_by(id=item).delete()
            db.session.commit()
        flash(f'Post: {post_user_filtered_list} has been removed', 'success')
        return redirect(url_for("postShop.posts"))
    else:
        flash("You do not have access to remove this post", 'error')
        return redirect(url_for("postShop.posts"))