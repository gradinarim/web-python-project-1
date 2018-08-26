import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

# Create 'users' table
def create_users_table():
    db.execute('''
        CREATE TABLE users (
            id SERIAL PRIMARY KEY,
            username VARCHAR NOT NULL,
            password VARCHAR NOT NULL
        );
    ''')
    db.commit()
    
    print('Created Users table.')
    
# Create 'books' table
def create_books_table():
    db.execute('''
        CREATE TABLE books (
            id SERIAL PRIMARY KEY,
            isbn VARCHAR NOT NULL,
            title VARCHAR NOT NULL,
            author VARCHAR NOT NULL,
            year VARCHAR NOT NULL
        );
    ''')
    db.commit()
    
    print('Created Books table.')
    
# Fill 'books' table from csv file
def insert_in_books_table(filename):
    f = open(filename)
    reader = csv.reader(f)
    
    i = 1
    
    for isbn, title, author, year in reader:
    
        db.execute('''
            INSERT INTO books 
            (isbn, title, author, year) 
            VALUES (:isbn, :title, :author, :year)''',
            {'isbn': isbn, 'title': title, 'author': author, 'year': year}
        )
        db.commit()
        
        print(f'{i} Added book {isbn}, {title}, {author}, {year}.')
        
        i += 1
    
# Create 'reviews' table
def create_reviews_table():
    db.execute('''
        CREATE TABLE reviews (
            id SERIAL PRIMARY KEY,
            book_id INTEGER REFERENCES books,
            user_id INTEGER REFERENCES users,
            rating INTEGER NOT NULL,
            review VARCHAR NOT NULL
        );
    ''')
    db.commit()
    
    print('Created Reviews table.')

# Create 'top_books' table
def create_top_books_table():
    db.execute('''
        CREATE TABLE top_books (
            id SERIAL PRIMARY KEY,
            book_id INTEGER REFERENCES books
        );
    ''')
    db.commit()
    print('Created Top Books table.')
    
def main():
    create_users_table()
    create_books_table()
    insert_in_books_table('books.csv')
    create_reviews_table()
    create_top_books_table()

if __name__ == "__main__":
    main()
