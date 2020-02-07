from app import db


class Product(db.Model):
    __tablename__ = 'product'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    price = db.Column(db.Float(), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String())
    image = db.Column(db.String())

    def __repr__(self):

        return f'{self.name} {self.price} {self.id}'


class Cart(db.Model):
    __tablename__ = 'cart'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='CASCADE'))
    product_id = db.Column(db.Integer(), db.ForeignKey('product.id', ondelete='CASCADE'))
    quantity = db.Column(db.Integer(), nullable=True)
