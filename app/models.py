from app import db


class Product(db.Model):
    __tablename__ = 'product'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    price = db.Column(db.Float())

    def __repr__(self):

        return f'Name: {self.name}   Price: {self.price}   [ID:{self.id}]'
