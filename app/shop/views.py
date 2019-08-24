from .. import db
from flask import render_template, request, url_for, redirect, flash, Blueprint
from flask_login import login_user, logout_user, login_required, current_user
from flask_user import roles_required
from app.forms import LoginForm, RegisterForm
from ..models import Product, User, Role, UserRoles
from colorama import Fore, Style  # test

shop = Blueprint('shop', __name__, template_folder='templates')


@shop.route('/')
def home():
    return render_template("home.html")


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
    users_list = db.session.query(User).all()
    if username is not None:
        profile = User.query.filter_by(username=username).first_or_404()
        role_temp_id = UserRoles.query.filter_by(user_id=profile.id).first().role_id
        role_name = Role.query.filter_by(id=role_temp_id).first().name
        print("ROLES", role_name)
        print('Profile', profile)
        return render_template("user.html", username=username, profile=profile, role=role_name)
    return render_template("users.html", users_list=users_list)


@shop.route('/role/<username>', methods=['GET', 'POST'])
def role(username):
    get_role_name = request.form.get("role")
    get_role_id = Role.query.filter_by(name=get_role_name).first().id
    print('Get role', get_role_id, get_role_name)
    user_id = User.query.filter_by(username=username).first().id
    db.session.query(UserRoles).filter(UserRoles.user_id == user_id).update({'role_id': get_role_id})
    db.session.commit()
    flash('Role has been changed',  'success')
    return redirect(url_for('shop.users'))


@shop.route('/products')
@login_required
def products():
    return render_template("products.html")


@shop.route('/remove')
@login_required
def remove():
    return render_template("delete.html")


@shop.route('/add', methods=['POST'])
def add():
    product_name = request.form['pr_name']
    product_price = request.form['pr_price']
    new_product = Product(name=product_name, price=product_price)
    if product_name == '' or product_price == '':
        flash('Enter product name and price', 'error')
    else:
        db.session.add(new_product)
        flash('Product %s (price: %s) has been added' % (product_name, product_price), 'success')
        db.session.commit()
    return redirect(url_for('shop.products'))


@shop.route('/delete', methods=['POST'])
def delete():
    product_remove = request.form['pr_name']
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
    return redirect(url_for('shop.remove'))


@shop.route('/list', methods=['GET'])
def shop_list():

    products_list = db.session.query(Product).all()
    products_name = db.session.query(Product.name).all()
    products_name = ([x[0] for x in products_name])
    products_price = db.session.query(Product.price).all()
    products_price = ([x[0] for x in products_price])
    products_id = db.session.query(Product.id).all()
    products_id = ([x[0] for x in products_id])
    print(Fore.YELLOW + 'PR_Name', products_name)  # test#
    print(Style.RESET_ALL)  # test
    if not products_name:
        flash('Product list is empty, add product to list', 'info')
    return render_template("shop_list.html", products_list=products_list,
                           products_name=products_name, products_price=products_price,
                           products_id=products_id)
