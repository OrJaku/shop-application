import os

from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])

db = SQLAlchemy(app)

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
    product_name = request.form['product']
    product = Product(name=product_name)
    db.session.add(product)
    db.session.commit()
    return redirect(url_for('products'))


@app.route('/delete', methods=['POST'])
def delete():
    products_list = db.session.query(Product).all()
    product_name = request.form['product']
    product = Product(name=product_name)
    if product == products_list:
        db.session.delete(product)
        db.session.commit()
    else:
        print('Brak produktu')
        print(products_list)
        print(product)
    return redirect(url_for('remove'))

@app.route('/shop', methods=['GET'])
def shop():
    products_list = db.session.query(Product).all()
    return render_template("shop.html", products_list=products_list)
