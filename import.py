from models import *
import csv
import os

from flask import Flask, render_template, request
from models import *
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)


def main():
    db.create_all()
    f = open("books.csv")
    reader = csv.reader(f)
    next(reader)
    for isbn, title, author, year in reader:
        book_check = Book.query.get(isbn)
        if book_check is None:
            book = Book(isbn=isbn, title=title,
                        author=author, year=int(year))
            db.session.add(book)
            print(f"Book added")
            print(f"\t Author: {author}")
            print(f"\t Title: {title}")
            print(f"\t Year: {year}")
            print(f"\t Isbn: {isbn}\n")
        else:
            print(f"Book with isbn:{isbn} already added")
    db.session.commit()


if __name__ == "__main__":
    with app.app_context():
        main()
