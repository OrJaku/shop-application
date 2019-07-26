from . import shop
from .. import db
from flask import render_template, request, url_for, redirect
from ..models import Product

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
    db.session.add(new_product)
    db.session.commit()
    return redirect(url_for('shop.products'))


@shop.route('/delete', methods=['POST'])
def delete():
    product_name = request.form['pr_name']
    if product_name == "del_all_prod":
        Product.query.filter().delete()
        db.session.commit()
    else:
        Product.query.filter_by(name=product_name).delete()
        print("Product", product_name)
        db.session.commit()
    return redirect(url_for('shop.remove'))


@shop.route('/list', methods=['GET'])
def shop_list():
    products_list = db.session.query(Product).all()
    print(products_list)
    return render_template("shop_list.html", products_list=products_list)
