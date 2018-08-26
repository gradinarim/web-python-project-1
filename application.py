import os
import configparser

from flask import Flask, session
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
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": GOODREADS_KEY, "isbns": "9781632168146"})
    return str(res.json())