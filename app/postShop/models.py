from app import db


class Posts(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(100), unique=True, nullable=False)
    post = db.Column(db.String(), nullable=False)
    user = db.Column(db.String(), nullable=False)
    time = db.Column(db.Float())
    time_date = db.Column(db.String())

    def __repr__(self):
        return f'{self.title} {self.post}'
