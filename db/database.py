import os
import psycopg2
from datetime import date

def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT", "5432"),
        database=os.getenv("DB_NAME", "postgres"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD")
    )

def init_db():
    # Таблица создаётся вручную в Supabase
    pass

def add_book(title: str, author: str, rating: int, user_id: int):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute('''
                INSERT INTO books (user_id, author, title, rating, read_date)
                VALUES (%s, %s, %s, %s, %s)
            ''', (user_id, author.strip(), title.strip(), rating, date.today()))

def get_books_by_year(user_id: int, year: str):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute('''
                SELECT title, author, rating, read_date
                FROM books
                WHERE user_id = %s AND EXTRACT(YEAR FROM read_date) = %s
                ORDER BY read_date ASC
            ''', (user_id, int(year)))
            return cursor.fetchall()

def delete_book_by_user_and_date(user_id: int, title: str, author: str, read_date: str):
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute('''
                DELETE FROM books
                WHERE user_id = %s AND title = %s AND author = %s AND read_date = %s
            ''', (user_id, title, author, read_date))
            return cursor.rowcount > 0
