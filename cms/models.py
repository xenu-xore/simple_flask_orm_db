from cms import db
# bcrypt_flask
from werkzeug.security import generate_password_hash
import datetime


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    registered_on = db.Column(db.DateTime, nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, login, password, admin=False):
        self.login = login
        self.password = generate_password_hash(password)
        print(self.password)
        self.registered_on = datetime.datetime.now()
        self.admin = admin

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def __repr__(self):
        return '<Users {}'.format(self.login)


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name_category = db.Column(db.String(255), nullable=True)
    article_one = db.relationship('Articles', backref='category', uselist=False)

    def __repr__(self,id, name_category):
        return "<Category %r %r>" % self.id, self.name_category

class Articles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=True)
    short_description = db.Column(db.String(255), nullable=False)
    article = db.Column(db.Text, nullable=True)
    date_publisher = db.Column(db.DateTime(), default=datetime.datetime.now())
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))

    def __repr__(self,id, name_category):
        return "<Articles %r %r>" % (self.id, self.article)

