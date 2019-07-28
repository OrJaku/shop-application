from . import shop
from .. import db
from flask import render_template, request, url_for, redirect, flash
from ..models import Product
from colorama import Fore, Style  # test

# db.create_all()
# db.drop_all()
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
        flash('Product %s (price: %s) hes been added' % (product_name, product_price), 'succes')
        db.session.commit()
    return redirect(url_for('shop.products'))


@shop.route('/delete', methods=['POST'])
def delete():
    product_name = request.form['pr_name']
    if product_name == "del_all_prod":
        Product.query.filter().delete()
        db.session.commit()
        flash('All products hes been removed from list', 'error')
    else:
        Product.query.filter_by(name=product_name).delete()
        print("Product %s hes been removed" % product_name)
        flash('Product %s hes been removed' % product_name, 'succes')
        db.session.commit()
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
        print('List is empty')
    return render_template("shop_list.html", products_list=products_list,
                           products_name=products_name, products_price=products_price,
                           products_id=products_id)
