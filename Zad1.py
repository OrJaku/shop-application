from flask import Flask, render_template, request, url_for, redirect

Zad1 = Flask(__name__)
list_p = []
@Zad1.route('/')
def home():
    return render_template("prodacts.html")


@Zad1.route('/prodacts', methods=['POST'])
def prodacts():
    prodact = request.form['prodact']
    list_p.append(prodact)
    return redirect(url_for('home'))



@Zad1.route('/shop', methods=['GET'])
def shop():

    return render_template("shop.html", list_p = list_p)
