from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app import db, login


class Product(db.Model):
    __tablename__ = 'product'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    price = db.Column(db.Float())

    def __repr__(self):

        return f'{self.name} {self.price} {self.id}'


class User(UserMixin, db.Model):
    __tablename__ = 'user'

    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(80), nullable=False)
    firstname = db.Column(db.String(80), unique=True, nullable=False)
    lastname = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    info = db.Column(db.String(160))

    @property
    def password(self):
        raise AttributeError("Attribute Error no.1")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):

        return check_password_hash(generate_password_hash, password)

    def __repr__(self):
        return f'{self.username} {self.email}'


@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
