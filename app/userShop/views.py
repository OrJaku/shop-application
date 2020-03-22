from .. import db
from flask import render_template, request, url_for, redirect, flash, Blueprint
from flask_login import login_user, logout_user, login_required, current_user
from app.userShop.forms import LoginForm, RegisterForm, ChangePasswordForm
from .models import User, Role, UserRoles
from ..postShop.models import Posts
from flask_dance.contrib.google import make_google_blueprint, google
import logging
import json


userShop = Blueprint('userShop', __name__, template_folder='templates')
with open('google_client.json') as f:
    data = json.load(f)
    client_id = (data[0]['client_id'])
    client_secret = (data[1]['client_secret'])
    google_oauth = make_google_blueprint(client_id=client_id,
                                         client_secret=client_secret,
                                         offline=True,
                                         scope=["profile", "email"])


def role_req(role_name):
    role_require_id = Role.query.filter_by(name=role_name).first().id
    return role_require_id


def current_role():
    current_role_id = UserRoles.query.filter_by(user_id=current_user.id).first().role_id
    return current_role_id


@userShop.route('/register', methods=["POST", "GET"])
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
            return redirect(url_for('userShop.register'))
        db.session.add(user)
        db.session.commit()
        flash('Registered successfully', 'success')
        logging.info("User %s", user)
        return redirect(url_for('userShop.login'))
    return render_template('register.html', title='Register', form=form)


@userShop.route('/login', methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('shop.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid login or password', 'error')
            return redirect(url_for('userShop.login'))
        login_user(user)
        flash('You are logged in as %s' % (db.session.query(User.username).first()), 'success')
        return redirect(url_for('shop.home'))
    return render_template('login.html', title='Sing In', form=form)


@userShop.route('/logout')
def logout():
    logout_user()
    flash('You are logged out', 'info')
    return redirect(url_for('shop.home'))


@userShop.route('/login/google', methods=['GET', 'POST'])
def google_login():
    if not google.authorized:
        return redirect(url_for("google.login"))
    resp = google.get('/oauth2/v2/userinfo')
    assert resp.ok, resp.text
    user_data = resp.json()
    user = User(email=user_data['email'], first_name=user_data['given_name'], last_name=user_data['family_name'])
    login_user(user)
    return render_template('home.html')


@userShop.route('/users', methods=['GET', 'POST'])
@userShop.route('/users/ <username>')
@login_required
def users(username=None):
    if current_role() == role_req('guest') or role_req('admin'):
        users_list = db.session.query(User).all()
        if username:
            user = User.query.filter_by(username=username).first_or_404()
            role_temp_id = UserRoles.query.filter_by(user_id=user.id).first().role_id
            role_name = Role.query.filter_by(id=role_temp_id).first().name
            logging.info("Role Name: %s", role_name)
            logging.info("User: %s", user)
            return render_template("user.html", username=username, user=user, role=role_name,
                                   current_role=current_role(), role_req=role_req('admin'))
        return render_template("users.html", users_list=users_list, current_role=current_role(),
                               role_req=role_req('admin'))
    else:
        flash("You do not have admin access", 'error')
        return render_template("home.html")


@userShop.route('/role/<username>', methods=['GET', 'POST'])
@login_required
def role(username):
    get_role_name = request.form.get("role")
    get_role_id = Role.query.filter_by(name=get_role_name).first().id
    user_id = User.query.filter_by(username=username).first().id
    db.session.query(UserRoles).filter(UserRoles.user_id == user_id).update({'role_id': get_role_id})
    db.session.commit()
    flash('\nRole has been changed',  'success')
    return redirect(url_for('userShop.users'))


@userShop.route('/profile/<username>', methods=['GET', 'POST'])
@login_required
def profile(username):
    user = User.query.filter_by(username=current_user.username).first_or_404()
    check_user = db.session.query(Posts.user).all()
    check_user = ([x[0] for x in check_user])
    if current_user.username in check_user:
        user_posts = Posts.query.filter_by(user=current_user.username).all()
        return render_template('profile.html', profile=user, posts=user_posts)
    else:
        return render_template('profile.html', profile=user)


@userShop.route('/change_password',  methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    return render_template('changepass.html', form=form)


@userShop.route('/changing',  methods=['GET', 'POST'])
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


@userShop.route('/remove_user', methods=['POST'])
@login_required
def remove_user():
    user = request.form['user']
    user_list = db.session.query(User.username).all()
    user_list = ([x[0] for x in user_list])
    logging.info("User List %s", user_list)
    if user == 'admin' or user not in user_list:
        flash('Invalid user', 'error')
    else:
        User.query.filter_by(username=user).delete()
        db.session.commit()
        flash(f'User: {user} has been removed', 'success')
    return redirect(url_for('userShop.users'))
