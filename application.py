import os
import configparser

from flask import Flask, session, render_template, request, redirect, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

import requests

config = configparser.ConfigParser()
config.read('config.cfg')
GOODREADS_KEY = config['Goodreadnes']['key']

app = Flask(__name__)

# Check for config variable
try:
    DATABASE_URL = config['Heroku']['url']
except Exception:
    print('DATABASE_URL is not set')

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(DATABASE_URL)
db = scoped_session(sessionmaker(bind=engine))

# Temporary class for books
class Book:
    def __init__(self, id, isbn, title, author, year):
        self.id = id
        self.isbn = isbn
        self.title = title
        self.author = author
        self.year = year

@app.route("/")
def index():

    # Get 20 top rated books for displaying on the main page
    top_books = db.execute('''
        SELECT * FROM books
        ORDER BY rating DESC
        LIMIT 20
    ''').fetchall()
    
    username = session.get('username', None)
    
    return render_template('index.html', top_books=top_books, username=username)
    
@app.route("/book/<int:book_id>")
def book(book_id):

    book = db.execute('''
        SELECT * FROM books
        WHERE id = :id
    ''', {'id': book_id}).fetchone()
    
    if not book:
        return render_template('error.html', message='We haven''t this book')

    return render_template('book.html', book=book)
    
@app.route("/registration", methods=['GET', 'POST'])
def registration():
    
    if request.method == 'GET':
        return render_template('registration.html')
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username and password:
            db.execute('''
                INSERT INTO users (username, password) VALUES (:username, :password)''',
                {'username': username, 'password': password}
            )
            db.commit()
            session['username'] = username
            return redirect(url_for('index'))
        else:
            # TODO: Show the error
            return redirect(url_for('registration'))
    
@app.route("/login", methods=['GET', 'POST'])
def login():

    if request.method == 'GET':
        return render_template('login.html')

    if request.method == 'POST':
    
        username = request.form.get("username")
        password = request.form.get("password")
    
        user_db = db.execute('''
            SELECT * FROM users WHERE username = :username;
        ''', {'username': username})
        
        if user_db.rowcount == 0:
            # TODO: Error message
            return redirect(url_for('login'))
        
        user = user_db.fetchone()
    
        if username == user.username and password == user.password:
            session['username'] = username
        
        return redirect(url_for('index'))
    
@app.route("/logout", methods=['GET'])
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))
    
    # res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": GOODREADS_KEY, "isbns": "9781632168146"})
    # return str(res.json())
    
    # {'books': [{'id': 29207858, 'isbn': '1632168146', 'isbn13': '9781632168146', 'ratings_count': 0, 'reviews_count': 2, 'text_reviews_count': 0, 'work_ratings_count': 26, 'work_reviews_count': 114, 'work_text_reviews_count': 10, 'average_rating': '4.04'}]}