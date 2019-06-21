from flask import Flask, render_template, request

Zad1 = Flask(__name__)
list_p = []
@Zad1.route('/')
def home():
    return render_template("home.html")


@Zad1.route('/prodacts')
def prodacts():
    return render_template("prodacts.html")
    r = request.get(Name)
    list_p.append(r)
@Zad1.route('/shop')
def shop():
    return render_template("shop.html", list_url=list_p)
    r.json()