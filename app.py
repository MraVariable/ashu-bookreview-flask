from flask import Flask, session, Response, render_template, request, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.sql.expression import func
import requests
from models import *
app = Flask(__name__)
app.secret_key = "I like fried rice"

# API key and other constants
key = "gSIbgf3YPonMEzxGvXOCg"
secret = 'enC3XCPgdy3IcRn3kejOaFeX2smblGIScNuaqFcQBw'
heading = "Ashu Book Review "
tag = "Don't judge a book by its cover, judge it by the reviews."


@app.route("/")
def index():
    # session['cur_user'] = None
    return render_template("landing.html", heading=heading, tag=tag)


@app.route("/login")
def login():
    return render_template("login.html", heading=heading, tag=tag)


@app.route("/logging", methods=["POST"])
def logging():
    username = request.form.get("username")
    checkuser = User.query.filter(User.username == username).first()
    if checkuser == None:
        return render_template("error.html", message="Username Not Found", heading=heading, tag=tag)
    pwd = request.form.get("pwd")
    if checkuser.password != pwd:
        print(checkuser.password)
        print(pwd)
        return render_template("error.html", message="Incorrect Password", heading=heading, tag=tag)
    session['cur_user'] = checkuser
    return render_template("search.html", cur_user=session['cur_user'], heading=heading, tag=tag)


@app.route("/register")
def register():
    return render_template("registration.html", heading=heading, tag=tag)


@app.route("/registering", methods=["POST"])
def registering():
    username = request.form.get("username")
    checkuser = User.query.filter(User.username == username).all()
    if checkuser:
        return render_template("error.html", message="Username Taken", heading=heading, tag=tag)
    uid = db.session.query(db.func.max(User.uid)).first()
    if not uid[0]:
        uid = 1
    else:
        uid = uid[0]+1
    pwd = request.form.get("pwd")
    newU = User(uid=uid, username=username, name=request.form.get(
        "name"), password=pwd)
    newU.add_user()
    session['cur_user'] = newU
    return render_template("search.html", cur_user=session['cur_user'], heading=heading, tag=tag)


@app.route("/results")
def results():
    books = None
    searchby = (request.args.get("searchby"))
    term = (request.args.get("term"))
    if searchby == "Author":
        books = Book.query.filter(Book.author.like(f'%{term}%')).all()
    elif searchby == "Title":
        books = Book.query.filter(Book.title.like(f'%{term}%')).all()
    elif searchby == "ISBN":
        books = Book.query.filter(Book.isbn.like(f'%{term}%')).all()
    else:
        return render_template("error.html", message="Internal Error", heading=heading, tag=tag)
    return render_template("results.html", cur_user=session['cur_user'], books=books, heading=heading, tag=tag)


@app.route("/book/<isbn>")
def book(isbn):
    book = Book.query.get(isbn)
    reviews = db.session.query(User.name, Review).filter(
        User.uid == Review.user_id, Review.book_id == isbn).all()
    res = requests.get(
        f'https://www.goodreads.com/book/review_counts.json?isbns={isbn}&key={key}')
    data = res.json()
    avg = data["books"][0]["average_rating"]
    num_review = data["books"][0]["ratings_count"]
    return render_template("book.html", cur_user=session['cur_user'], book=book, avg=avg, num_review=num_review, reviews=reviews, heading=heading, tag=tag)


@app.route("/post/<isbn>")
def post(isbn):
    book = Book.query.get(isbn)
    cur_user = session['cur_user']
    book.add_review(uid=cur_user.uid, stars=request.args.get(
        "stars"), body=request.args.get("text"))

    book = Book.query.get(isbn)
    reviews = db.session.query(User.name, Review).filter(
        User.uid == Review.user_id, Review.book_id == isbn).all()
    res = requests.get(
        f'https://www.goodreads.com/book/review_counts.json?isbns={isbn}&key={key}')
    data = res.json()
    avg = data["books"][0]["average_rating"]
    num_review = data["books"][0]["ratings_count"]
    return render_template("book.html", cur_user=session['cur_user'], book=book, avg=avg, num_review=num_review, reviews=reviews, heading=heading, tag=tag)


@app.route("/api/<string:isbn>")
def book_api(isbn):
    book = Book.query.get(isbn)
    if book is None:
        return jsonify({"error": "Invalid ISBN"}), 404
    res = requests.get(
        f'https://www.goodreads.com/book/review_counts.json?isbns={isbn}&key={key}')
    data = res.json()
    avg = data["books"][0]["average_rating"]
    num_review = data["books"][0]["ratings_count"]
    return jsonify({
        "title": book.title,
        "author": book.author,
        "year": book.year,
        "isbn": isbn,
        "review_count": num_review,
        "average_score": avg
    })


if __name__ == '__main__':
    app.run()
