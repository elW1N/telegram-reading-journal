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

def get_books_count_by_year(user_id: int) -> dict:
    """Возвращает словарь: {год: количество книг} для пользователя."""
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute('''
                SELECT EXTRACT(YEAR FROM read_date) AS year, COUNT(*) AS count
                FROM books
                WHERE user_id = %s
                GROUP BY year
                ORDER BY year DESC
            ''', (user_id,))
            return {int(year): count for year, count in cursor.fetchall()}
        
def get_all_years(user_id: int) -> list[str]:
    """Возвращает список годов (в виде строк), в которые пользователь читал книги."""
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute('''
                SELECT DISTINCT EXTRACT(YEAR FROM read_date) AS year
                FROM books
                WHERE user_id = %s
                ORDER BY year DESC
            ''', (user_id,))
            return [str(int(row[0])) for row in cursor.fetchall()]