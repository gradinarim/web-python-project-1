import sys
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


@app.route("/")
def index():

    # Get 20 top rated books for displaying on the main page
    top_books = db.execute('''
        SELECT * FROM books
        ORDER BY rating DESC
        LIMIT 20
    ''').fetchall()

    # Get session for user
    user = session.get('user', None)
    
    return render_template('index.html', top_books=top_books, user=user)
    
    
@app.route("/book/<int:book_id>")
def book(book_id):

    book = db.execute('''
        SELECT * FROM books
        WHERE id = :id
    ''', {'id': book_id}).fetchone()
    
    isbn = book.isbn
    
    # Get Goodreads rating
    result = requests.get('https://www.goodreads.com/book/review_counts.json', params={'key': GOODREADS_KEY, 'isbns': isbn})
    if result:
        gr_rating = result.json()
        gr_work_ratings_count = gr_rating['books'][0]['work_ratings_count']
        gr_average_rating = float(gr_rating['books'][0]['average_rating'])
    else:
        gr_work_ratings_count = 0
        gr_average_rating = 0
    
    if book.rating != gr_average_rating:
        db.execute('''
            UPDATE books SET rating = :rating WHERE id = :id
        ''', {'rating': gr_average_rating, 'id': book.id})
        db.commit()
        
        book = db.execute('''
            SELECT * FROM books
            WHERE id = :id
        ''', {'id': book_id}).fetchone()
    
    if not book:
        return render_template('error.html', message='We haven\'t this book')

    user = session.get('user', None)
    
    is_reviewed = False
    if user:
        user_review = db.execute('''
            SELECT * FROM reviews
            WHERE user_id = :user_id AND book_id = :book_id
        ''', {'user_id': user['id'], 'book_id': book.id}).fetchone()
        
        if user_review:
            is_reviewed = True
        
    return render_template('book.html', book=book, user=user)
    
    
@app.route("/registration", methods=['GET', 'POST'])
def registration():
    
    if request.method == 'GET':
        session.pop('user', None)
        return render_template('registration.html')
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username and password:
            db.execute('''
                INSERT INTO users (username, password) VALUES (:username, :password)
            ''', {'username': username, 'password': password})
            db.commit()
            
            # Get id of created user
            user = db.execute('''
                SELECT * FROM users WHERE username = :username
            ''', {'username': username}).fetchone()
            
            # Write in session id and name of user
            session['user'] = {'id': user.id, 'name': user.username}
            
            return redirect(url_for('index'))
            
        else:
            # TODO: Show the error
            return redirect(url_for('registration'))
    
    
@app.route("/login", methods=['GET', 'POST'])
def login():

    if request.method == 'GET':
        session.pop('user', None)
        return render_template('login.html')

    if request.method == 'POST':
    
        username = request.form.get("username")
        password = request.form.get("password")
    
        user = db.execute('''
            SELECT * FROM users WHERE username = :username
        ''', {'username': username}).fetchone()
        
        if not user:
            # TODO: Error message
            return redirect(url_for('login'))
    
        if password == user.password:
            session['user'] = {'id': user.id, 'name': user.username}
        else:
            # TODO: Error message
            return redirect(url_for('login'))
        
        return redirect(url_for('index'))
    
    
@app.route("/logout", methods=['GET'])
def logout():

    session.pop('user', None)
    return redirect(url_for('index'))
    
    