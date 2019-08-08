from .. import db
from flask import render_template, request, url_for, redirect, flash
from ..models import Product
from colorama import Fore, Style  # test
from flask import Blueprint

shop = Blueprint('shop', __name__, template_folder='templates')


@shop.route('/')
def home():
    return render_template("home.html")


@shop.route('/products')
def products():
    return render_template("products.html")


@shop.route('/remove')
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
        flash('Product %s (price: %s) has been added' % (product_name, product_price), 'succes')
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
            flash('Product %s has been removed' % product_remove, 'succes')
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
