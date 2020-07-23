import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy()
with app.app_context():
    db.init_app(app)


class User(db.Model):
    __tablename__ = "users"
    uid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)

    def add_user(self):
        db.session.add(self)
        db.session.commit()
        print("User added")


class Book(db.Model):
    __tablename__ = "books"
    isbn = db.Column(db.String, primary_key=True)
    title = db.Column(db.String, nullable=False)
    author = db.Column(db.String, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    reviews = db.relationship("Review", backref="books", lazy=True)

    def add_review(self, uid, stars, body):
        review = Review(book_id=self.isbn, user_id=uid,
                        stars=stars, body=body)
        db.session.add(review)
        db.session.commit()


class Review(db.Model):
    __tablename__ = "reviews"
    rid = db.Column(db.Integer, primary_key=True)
    stars = db.Column(db.Integer, nullable=False)
    body = db.Column(db.String, nullable=False)
    book_id = db.Column(db.String, db.ForeignKey(
        "books.isbn"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.uid"), nullable=False)
