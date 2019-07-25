from app import app
from app import db
from flask import render_template, request, url_for, redirect
from .models import Product

# db.create_all()
# db.drop_all()
@app.route('/')
def home():
    return render_template("home.html")


@app.route('/products')
def products():
    return render_template("products.html")


@app.route('/remove')
def remove():
    return render_template("delete.html")


@app.route('/add', methods=['POST'])
def add():
    product_name = request.form['pr_name']
    product_price = request.form['pr_price']
    new_product = Product(name=product_name, price=product_price)
    db.session.add(new_product)
    db.session.commit()
    return redirect(url_for('products'))


@app.route('/delete', methods=['POST'])
def delete():
    product_name = request.form['pr_name']
    Product.query.filter_by(name=product_name).delete()
    print("Product", product_name)
    db.session.commit()
    return redirect(url_for('remove'))


@app.route('/shop', methods=['GET'])
def shop():
    products_list = db.session.query(Product).all()
    print(products_list)
    return render_template("shop.html", products_list=products_list)
