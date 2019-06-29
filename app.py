from flask import Flask, render_template, request, url_for, redirect

app = Flask(__name__)
products_list = []
@app.route('/')
def home():
    return render_template("home.html")


@app.route('/products')
def products():
    return render_template("products.html")


@app.route('/add', methods=['POST'])
def add():
    product = request.form['product']
    products_list.append(product)
    return redirect(url_for('products'))



@app.route('/shop', methods=['GET'])
def shop():

    return render_template("shop.html", products_list = products_list)
