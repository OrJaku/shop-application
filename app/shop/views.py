from .. import db
from flask import render_template, request, url_for, redirect, flash, Blueprint
from flask_login import login_required, current_user
from .models import Product, Cart
from ..userShop.views import current_role, role_req
import sqlalchemy.exc
import time
import logging
import io
import csv
import json
import random

shop = Blueprint('shop', __name__, template_folder='templates')

logging.basicConfig(level=logging.INFO)


@shop.route('/', methods=['GET'])
def home():
    products = db.session.query(Product.id).all()
    products = ([n[0] for n in products])
    products_list = []
    for product in products:
        product = Product.query.filter_by(id=product).first()
        products_list.append(product)
    random_numbers = random.sample([i for i in range(len(products_list))], k=len(products_list))
    list_with_rnd_numbers = []
    for x, y in zip(random_numbers, products_list):
        result = (x, y)
        list_with_rnd_numbers.append(result)
    sorted_list = sorted(list_with_rnd_numbers)
    rnd_products_list = []
    for x, y in sorted_list:
        rnd_products_list.append(y)
    try:
        first_product = rnd_products_list[0]
    except IndexError:
        flash('There is no product there', 'success')
        first_product = []
    try:
        products_list_1 = rnd_products_list[1:4]
    except IndexError:
        products_list_1 = []
    try:
        products_list_2 = rnd_products_list[4:7]
    except IndexError:
        products_list_2 = []
    try:
        products_list_3 = rnd_products_list[7:10]
    except IndexError:
        products_list_3 = []

    return render_template("home.html", products_list_1=products_list_1, products_list_2=products_list_2,
                           products_list_3=products_list_3, first_product=first_product)


@shop.route('/add', methods=['POST'])
def add():
    prod_name = request.form['product_name']
    prod_price = request.form['product_price']
    prod_quantity = request.form['product_quantity']
    new_product = Product(name=prod_name, price=prod_price, quantity=prod_quantity)
    if prod_name == '' or prod_price == '' or prod_quantity == '':
        flash('Enter product name, price and quantity', 'error')
    else:
        db.session.add(new_product)
        flash('Product %s (price: %s) has been added' % (prod_name, prod_price), 'success')
        db.session.commit()
    return redirect(url_for('shop.shop_list'))


@shop.route('/delete', methods=['POST'])
def delete():
    product_id = int(request.form['product_id'])
    products_list = db.session.query(Product.id).all()
    products_list = ([x[0] for x in products_list])
    if product_id in products_list:
        Product.query.filter_by(id=product_id).delete()
        flash('Product %s has been removed' % product_id, 'success')
        db.session.commit()
    else:
        flash('Product %s is not on list' % product_id, 'error')
    return redirect(url_for('shop.shop_list'))


@shop.route('/add_product_img', methods=['POST'])
def add_product_img():
    new_image = request.form['product_image_link']
    product_id = request.form['product_id']
    product = Product.query.filter_by(id=product_id).first()
    product.image = new_image
    db.session.add(product)
    db.session.commit()
    if current_user.is_authenticated:
        return render_template('product.html', product=product, current_role=current_role(), role_req=role_req('admin'))
    else:
        return render_template('product.html', product=product)


@shop.route('/delete_selected', methods=['POST'])
def delete_selected():
    product_list_remove = request.form.getlist("remove_product")
    print("LIST", product_list_remove)
    for product_id in product_list_remove:
        Product.query.filter_by(id=product_id).delete()
        db.session.commit()
    return redirect(url_for('shop.shop_list'))


@shop.route('/import_products', methods=['GET', 'POST'])
def import_products():
    if request.method == "POST":
        updated_file = request.files['file']
        if not updated_file:
            flash("You didn't choose CSV/JSON file or file is empty", 'info')
            return redirect(url_for('shop.shop_list'))
        else:
            file_name = updated_file.filename
            extension = file_name.split('.')[-1]
            print("TEST0", updated_file)
            if extension == "csv":
                stream = io.StringIO(updated_file.stream.read().decode("utf-8"), newline=None)
                data_file = list(csv.reader(stream, delimiter=','))
                for row in data_file[1:]:
                    if row[0] == "" or row[1] == "" or row[2] == "":
                        flash('Some cells in file are empty, please check fill of columns and rows'
                              '(product name, price and quantity)', 'error')
                    else:
                        try:
                            new_product = Product(name=row[0], price=row[1], quantity=row[2], description=row[3],
                                                  image=row[4])
                            db.session.add(new_product)
                            db.session.commit()
                        except sqlalchemy.exc.DataError:
                            flash("Data problem, products have not been added - check column fill correctness", 'error')
                        except IndexError:
                            flash("Data problem, some column is empty", 'error')
                flash('Added {} product/s' .format(len(data_file[1:])), 'success')
                return redirect(url_for('shop.shop_list'))
            elif extension == "json":
                stream = json.load(updated_file)
                print(stream)
                return redirect(url_for('shop.shop_list'))
            else:
                return redirect(url_for('shop.shop_list'))
    return redirect(url_for('shop.shop_list'))


@shop.route('/export_products', methods=['POST'])
def export_products():
    products_id = db.session.query(Product.id).all()
    time_data = time.strftime("%Y%m%d-%H%M%S")
    export_format = request.form['format']
    if export_format == 'csv':
        products_to_csv = []
        with open('output/product_list_%s.csv' % time_data, mode='w') as csv_file:
            new_row = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            first_row = [
                "ID",
                "Name",
                "Price",
                "Quantity",
                "Description",
                "Image link",
                ]
            new_row.writerow(first_row)
            for product_id in products_id:
                product = Product.query.filter_by(id=product_id).first()
                prod_id = product.id
                prod_name = product.name
                prod_price = product.price
                prod_quantity = product.quantity
                prod_description = product.description
                prod_image_link = product.image
                product_to_csv = [
                    prod_id,
                    prod_name,
                    prod_price,
                    prod_quantity,
                    prod_description,
                    prod_image_link,
                ]
                new_row.writerow(product_to_csv)
                products_to_csv.append(product_to_csv)
            flash('You exported products list to CSV file "product_list_%s.csv"' % time_data, 'success')
            return redirect(url_for('shop.shop_list'))
    elif export_format == 'json':
        with open('output/product_list_%s.json' % time_data, mode='w') as json_file:
            output = []
            for product_id in products_id:
                product = Product.query.filter_by(id=product_id).first()
                new_json_product = {
                    'id': product.id,
                    'name': product.name,
                    'price': product.price,
                    'quantity': product.quantity,
                    'description': product.description,
                    'image link': product.image,
                }
                output.append(new_json_product)
            json.dump(output, json_file)
        flash('You exported products list to JSON file "product_list_%s.json"' % time_data, 'success')
        return redirect(url_for('shop.shop_list'))
    else:
        return redirect(url_for('shop.shop_list'))


@shop.route('/list', methods=['GET', 'POST'])
@shop.route('/list/<product>')
def shop_list(product=None):
    if product is None:
        products_id = db.session.query(Product.id).all()
        products_id = ([x[0] for x in products_id])
        products_id = sorted(products_id)
        if request.method == "POST":
            sort = request.form['sort']
            if sort == "sort_name":
                products_name = []
                for id_ in products_id:
                    product_name = Product.query.filter_by(id=id_).first().name
                    products_name.append(product_name)
                products_name = sorted(products_name)
                products_id = []
                for name in products_name:
                    product_id = Product.query.filter_by(name=name).first().id
                    products_id.append(product_id)
            elif sort == "sort_id":
                products_id = sorted(products_id)
            else:
                pass
        products_list = []
        for i in products_id:
            product = Product.query.filter_by(id=i).first()
            products_list.append(product)
        # logging.info("Products list %s", products_list)
        if not products_list:
            flash('Product list is empty', 'info')
        if current_user.is_authenticated:
            return render_template("shop_list.html", current_role=current_role(),
                                   role_req=role_req('admin'), products_list=products_list)
        else:
            return render_template("shop_list.html", products_list=products_list)
    else:
        product = Product.query.filter_by(name=product).first()
        if current_user.is_authenticated:
            return render_template('product.html', product=product, current_role=current_role(),
                                   role_req=role_req('admin'))
        else:
            return render_template('product.html', product=product)


@shop.route('/product_quantity', methods=['GET', 'POST'])
def product_quantity():
    product_id = request.form['product_id']
    new_quantity = request.form['new_quantity']
    product = Product.query.filter_by(id=product_id).first()
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
    product_id = request.form['product_id']
    product = Product.query.filter_by(id=product_id).first()
    product.description = new_description
    db.session.add(product)
    db.session.commit()
    if current_user.is_authenticated:
        return render_template('product.html', product=product, current_role=current_role(), role_req=role_req('admin'))
    else:
        return render_template('product.html', product=product)


@shop.route('/cart', methods=["POST", "GET"])
@login_required
def cart():
    current_cart_unfiltered_id = db.session.query(Cart.product_id)
    current_cart_id = current_cart_unfiltered_id.filter_by(user_id=current_user.id)
    user_cart_list_id = ([x[0] for x in current_cart_id])
    user_cart_list = []
    product = None
    for product_id in user_cart_list_id:
        product = Product.query.filter_by(id=product_id).first()
        user_cart_list.append(product)
    if request.method == "POST":
        product_id = request.form['product_id']
        if int(product_id) in user_cart_list_id:
            flash(f'This product is already in your shopping cart', 'info')
            return render_template("product.html", product=product)
        else:
            product = Product.query.filter_by(id=product_id).first()
            product_id = product.id
            user_id = current_user.id
            new_product = Cart(user_id=user_id, product_id=product_id, quantity=1)
            db.session.add(new_product)
            db.session.commit()
            return redirect(url_for("shop.cart"))
    else:
        return render_template("cart.html", user_cart_list=user_cart_list)


@shop.route('/clear_cart', methods=["POST"])
def clear_cart():
    cart_products = Cart.query.filter_by(user_id=current_user.id)
    cart_products.delete()
    db.session.commit()
    return redirect(url_for("shop.cart"))


@shop.route('/buy', methods=["POST"])
def buy():
    buying_quantity = 1
    cart_products = Cart.query.filter_by(user_id=current_user.id)
    flash('You bought:', 'success')
    for products in cart_products:
        product = Product.query.filter_by(id=products.product_id).first()
        update_quantity = product.quantity - buying_quantity
        product.quantity = update_quantity
        cart_products.delete()
        db.session.commit()
        flash(f'{product.name}', 'success')
    return redirect(url_for("shop.cart"))
