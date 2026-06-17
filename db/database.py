import os
import psycopg2
from datetime import date


def get_conn():
    return psycopg2.connect(os.getenv("DATABASE_URL"))

def init_db():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id SERIAL PRIMARY KEY,
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
        VALUES (%s, %s, %s, %s, %s)
    ''', (user_id, author.strip(), title.strip(), rating, date.today().isoformat()))
    conn.commit()
    conn.close()

def get_books_by_year(user_id: int, year: str):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT title, author, rating, read_date
        FROM books
        WHERE user_id = %s AND EXTRACT(YEAR FROM read_date::date)::TEXT = %s
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
        WHERE user_id = %s AND title = %s AND author = %s AND read_date = %s
    ''', (user_id, title, author, read_date))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted

def get_books_count_by_year(user_id: int) -> dict:
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT EXTRACT(YEAR FROM read_date::date)::TEXT AS year, COUNT(*) AS count
        FROM books
        WHERE user_id = %s
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
        SELECT DISTINCT EXTRACT(YEAR FROM read_date::date)::TEXT AS year
        FROM books
        WHERE user_id = %s
        ORDER BY year DESC
    ''', (user_id,))
    years = [row[0] for row in cursor.fetchall()]
    conn.close()
    return years
