from .. import db
from flask import render_template, request, url_for, redirect, flash, Blueprint
from flask_login import login_user, logout_user, login_required, current_user
from app.forms import LoginForm, RegisterForm, ChangePasswordForm
from ..models import Product, User, Role, UserRoles, Posts, Cart
import time
from colorama import Fore, Style  # test

shop = Blueprint('shop', __name__, template_folder='templates')


def role_req(role_name):
    role_require_id = Role.query.filter_by(name=role_name).first().id
    return role_require_id


def current_role():
    current_role_id = UserRoles.query.filter_by(user_id=current_user.id).first().role_id
    return current_role_id


@shop.route('/', methods=['GET'])
def home():
    title = db.session.query(Posts.title).all()
    title = ([x[0] for x in title])
    posts_list = []
    for item in title:
        posts_list.append(item)
    if not posts_list:
        return render_template("home.html")
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
    i = 0
    if len(posts_list) == 0 or len(posts_list) == 1:
        return render_template("home.html", title=title, post=post, user=user, post_id=post_id, time=time_date)
    elif len(posts_list) == 2:
        page_post2 = posts_list[0]
        post2 = Posts.query.filter_by(title=page_post2).first()
        posts_list2.append(post2)
    else:
        while i != len(posts_list) - 1:
            i += 1
            page_post2 = posts_list[len(posts_list) - (i+1)]
            post2 = Posts.query.filter_by(title=page_post2).first()
            posts_list2.append(post2)
    return render_template("home.html", title=title, post=post, user=user, time=time_date,
                           post_id=post_id, posts_list2=posts_list2)


@shop.route('/register', methods=["POST", "GET"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(first_name=form.first_name.data,
                    last_name=form.last_name.data,
                    username=form.username.data,
                    email=form.email.data,
                    password=form.password.data,
                    role=[Role.query.filter_by(name='guest').first()])

        if len(form.password.data) < 6:
            flash('Password is too short', 'error')
            return redirect(url_for('shop.register'))
        db.session.add(user)
        db.session.commit()
        flash('Registered successfully', 'success')
        print(Fore.YELLOW + 'user', user)  # test#
        print(Style.RESET_ALL)  # test
        return redirect(url_for('shop.login'))
    return render_template('register.html', title='Register', form=form)


@shop.route('/login', methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('shop.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid login or password', 'error')
            return redirect(url_for('shop.login'))
        login_user(user)
        flash('You are logged in as %s' % (db.session.query(User.username).first()), 'success')
        return redirect(url_for('shop.home'))
    return render_template('login.html', title='Sing In', form=form)


@shop.route('/logout')
def logout():
    logout_user()
    flash('You are logged out', 'info')
    return redirect(url_for('shop.home'))


@shop.route('/users', methods=['GET', 'POST'])
@shop.route('/users/ <username>')
@login_required
def users(username=None):
    if current_role() == role_req('guest') or role_req('admin'):
        users_list = db.session.query(User).all()
        if username is not None:
            user = User.query.filter_by(username=username).first_or_404()
            role_temp_id = UserRoles.query.filter_by(user_id=user.id).first().role_id
            role_name = Role.query.filter_by(id=role_temp_id).first().name
            print("Roles", role_name)
            print('Profile', user)
            return render_template("user.html", username=username, user=user, role=role_name,
                                   current_role=current_role(), role_req=role_req('admin'))
        return render_template("users.html", users_list=users_list, current_role=current_role(),
                               role_req=role_req('admin'))
    else:
        flash("You do not have admin access", 'error')
        return render_template("home.html")


@shop.route('/role/<username>', methods=['GET', 'POST'])
@login_required
def role(username):
    get_role_name = request.form.get("role")
    get_role_id = Role.query.filter_by(name=get_role_name).first().id
    # print('Get role', get_role_id, get_role_name)
    user_id = User.query.filter_by(username=username).first().id
    db.session.query(UserRoles).filter(UserRoles.user_id == user_id).update({'role_id': get_role_id})
    db.session.commit()
    flash('\nRole has been changed',  'success')
    return redirect(url_for('shop.users'))


@shop.route('/profile/<username>', methods=['GET', 'POST'])
@login_required
def profile(username):
    user = User.query.filter_by(username=current_user.username).first_or_404()
    check_user = db.session.query(Posts.user).all()
    check_user = ([x[0] for x in check_user])
    if current_user.username in check_user:
        posts = Posts.query.filter_by(user=current_user.username).all()
        return render_template('profile.html', profile=user, posts=posts)
    else:
        return render_template('profile.html', profile=user)


@shop.route('/change_password',  methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    return render_template('changepass.html', form=form)


@shop.route('/changing',  methods=['GET', 'POST'])
@login_required
def changing():
    form = ChangePasswordForm()
    old_password = form.old_password.data
    new_password = form.new_password.data
    confirm_password = form.conf_password.data
    user = User.query.filter_by(username=current_user.username).first()
    check_password = user.check_password(old_password)
    if check_password is True:
        if new_password != confirm_password:
            flash('New password and confirm password need to be the same', 'error')
        else:
            user.password = new_password
            db.session.add(user)
            db.session.commit()
            flash('Password has been changed', 'success')
    elif check_password is False:
        flash('Old  password is wrong', 'error')
    return render_template('profile.html', form=form, profile=current_user)


@shop.route('/remove_user', methods=['POST'])
@login_required
def remove_user():
    user = request.form['user']
    user_list = db.session.query(User.username).all()
    user_list = ([x[0] for x in user_list])
    print("user list", user_list)
    if user == 'admin' or user not in user_list:
        flash('Invalid user', 'error')
    else:
        User.query.filter_by(username=user).delete()
        db.session.commit()
        flash(f'User: {user} has been removed', 'success')
    return redirect(url_for('shop.users'))


@shop.route('/add', methods=['POST'])
def add():
    product_name = request.form['product_name']
    product_price = request.form['product_price']
    new_product = Product(name=product_name, price=product_price)
    if product_name == '' or product_price == '':
        flash('Enter product name and price', 'error')
    else:
        db.session.add(new_product)
        flash('Product %s (price: %s) has been added' % (product_name, product_price), 'success')
        db.session.commit()
    return redirect(url_for('shop.shop_list'))


@shop.route('/delete', methods=['POST'])
def delete():
    product_remove = request.form['product']
    if product_remove == "del_all_prod":
        Product.query.filter().delete()
        db.session.commit()
        flash('All products has been removed from list', 'error')
    else:
        products_list = db.session.query(Product.name).all()
        products_list = ([x[0] for x in products_list])
        if product_remove in products_list:
            Product.query.filter_by(name=product_remove).delete()
            flash('Product %s has been removed' % product_remove, 'success')
            db.session.commit()
        else:
            flash('Product %s is not on list' % product_remove, 'error')
    return redirect(url_for('shop.shop_list'))


@shop.route('/list', methods=['GET', 'POST'])
@shop.route('/list/<product>')
def shop_list(product=None):
    if product is None:
        products_list = db.session.query(Product).all()
        products_name = db.session.query(Product.name).all()
        products_name = ([x[0] for x in products_name])
        products_price = db.session.query(Product.price).all()
        products_price = ([x[0] for x in products_price])
        products_id = db.session.query(Product.id).all()
        products_id = ([x[0] for x in products_id])
        products_quantity = db.session.query(Product.quantity).all()
        products_quantity = ([x[0] for x in products_quantity])
        print(Fore.YELLOW + 'PR_Name', products_name)  # test#
        print(Style.RESET_ALL)  # test
        if not products_name:
            flash('Product list is empty', 'info')
        if current_user.is_authenticated:
            return render_template("shop_list.html", products_list=products_list,
                                   products_name=products_name, products_price=products_price, products_id=products_id,
                                   products_quantity=products_quantity, current_role=current_role(),
                                   role_req=role_req('admin'))
        else:
            return render_template("shop_list.html", products_list=products_list, products_quantity=products_quantity,
                                   products_name=products_name, products_price=products_price, products_id=products_id)
    else:
        product = Product.query.filter_by(name=product).first()
        if current_user.is_authenticated:
            return render_template('product.html', product=product, current_role=current_role(),
                                   role_req=role_req('admin'))
        else:
            return render_template('product.html', product=product)


@shop.route('/product_quantity', methods=['GET', 'POST'])
def product_quantity():
    product = request.form['product_quantity']
    new_quantity = request.form['new_quantity']
    product = Product.query.filter_by(name=product).first()
    product.quantity = new_quantity
    db.session.add(product)
    db.session.commit()
    if current_user.is_authenticated:
        return render_template('product.html', product=product, current_role=current_role(), role_req=role_req('admin'))
    else:
        return render_template('product.html', product=product)


@shop.route('/add_description/', methods=['GET', 'POST'])
def add_description():
    new_description = request.form['description']
    product = request.form['product']
    product = Product.query.filter_by(name=product).first()
    # print("New description", new_description)
    product.description = new_description
    db.session.add(product)
    db.session.commit()
    if current_user.is_authenticated:
        return render_template('product.html', product=product, current_role=current_role(), role_req=role_req('admin'))
    else:
        return render_template('product.html', product=product)


@shop.route('/add_post', methods=['POST'])
def add_post():
    title_list = db.session.query(Posts.title).all()
    title_list = ([x[0] for x in title_list])
    title = request.form['title']
    if not title:
        flash("You have to add title", 'error')
        return redirect(url_for('shop.home'))
    elif title in title_list:
        flash("Post with the same title does exist", 'error')
        return redirect(url_for('shop.home'))
    post = request.form['post']
    if not post:
        flash("You have to add some text", 'error')
        return redirect(url_for('shop.home'))
    if current_user.is_anonymous:
        user = "Guest"
    else:
        user = current_user.username
    seconds = time.time()
    time_date = time.ctime(seconds)
    new_post = Posts(title=title, post=post, user=user, time=seconds, time_date=time_date)
    db.session.add(new_post)
    db.session.commit()
    return redirect(url_for('shop.home'))


@shop.route('/remove_post', methods=['GET', 'POST'])
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
            post_user_list.append(post_user)  # post.user
    if current_role() == role_req('admin'):
        if request.method == "POST":
            if 'all_posts_remove' in rem_post:
                Posts.query.filter().delete()
                db.session.commit()
            else:
                print("Posts to remove:", rem_post)
                for item in rem_post:
                    Posts.query.filter_by(id=item).delete()
                    db.session.commit()
                flash(f'Post: {rem_post} has been removed', 'success')
            return redirect(url_for('shop.home'))
    elif user in post_user_list:
        for item in rem_post:
            post_user = Posts.query.filter_by(id=item).first().user
            print("user post", post_user)
            if post_user == user:
                post_user_filtered_list.append(item)
        print('post_user_filtered_list', post_user_filtered_list)
        for item in post_user_filtered_list:
            Posts.query.filter_by(id=item).delete()
            db.session.commit()
        flash(f'Post: {post_user_filtered_list} has been removed', 'success')
        return redirect(url_for("shop.home"))
    else:
        flash("You do not have access to remove this post", 'error')
        return redirect(url_for("shop.home"))


@shop.route('/cart', methods=["POST", "GET"])
def cart():
    ip = request.remote_addr
    cart_list_unfiltered_id = db.session.query(Cart.product_id)
    cart_list_id = cart_list_unfiltered_id.filter_by(user_id=current_user.id)
    user_cart_list_id = ([x[0] for x in cart_list_id])
    user_cart_list = []
    for product_id in user_cart_list_id:
        product_name = Product.query.filter_by(id=product_id).first()
        user_cart_list.append(product_name)
    if request.method == "POST":
        product_name = request.form['product']
        product = Product.query.filter_by(name=product_name).first()
        product_id = product.id
        user_id = current_user.id
        new_product = Cart(user_id=user_id, product_id=product_id)
        db.session.add(new_product)
        db.session.commit()
        return render_template("cart.html", user_cart_list=user_cart_list, ip=ip)
    else:
        return render_template("cart.html", ip=ip, user_cart_list=user_cart_list)


@shop.route('/buying', methods=["POST"])
def buying():
    products_name = request.form['cart']
    print(products_name)
    return redirect(url_for("shop.cart"))
