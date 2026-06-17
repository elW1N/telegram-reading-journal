import os
import sqlite3
from datetime import date

DB_PATH = os.getenv("DB_PATH", "/app/data/books.db")

def get_conn():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            author TEXT NOT NULL,
            title TEXT NOT NULL,
            rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
            read_date TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def add_book(title: str, author: str, rating: int, user_id: int):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO books (user_id, author, title, rating, read_date)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, author.strip(), title.strip(), rating, date.today().isoformat()))
    conn.commit()
    conn.close()

def get_books_by_year(user_id: int, year: str):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT title, author, rating, read_date
        FROM books
        WHERE user_id = ? AND strftime('%Y', read_date) = ?
        ORDER BY read_date ASC
    ''', (user_id, year))
    books = cursor.fetchall()
    conn.close()
    return books

def delete_book_by_user_and_date(user_id: int, title: str, author: str, read_date: str):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute('''
        DELETE FROM books
        WHERE user_id = ? AND title = ? AND author = ? AND read_date = ?
    ''', (user_id, title, author, read_date))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted

def get_books_count_by_year(user_id: int) -> dict:
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT strftime('%Y', read_date) AS year, COUNT(*) AS count
        FROM books
        WHERE user_id = ?
        GROUP BY year
        ORDER BY year DESC
    ''', (user_id,))
    result = {int(year): count for year, count in cursor.fetchall()}
    conn.close()
    return result

def get_all_years(user_id: int) -> list[str]:
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT DISTINCT strftime('%Y', read_date) AS year
        FROM books
        WHERE user_id = ?
        ORDER BY year DESC
    ''', (user_id,))
    years = [row[0] for row in cursor.fetchall()]
    conn.close()
    return years
