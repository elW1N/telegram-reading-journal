import sqlite3
from datetime import date
from pathlib import Path


DB_PATH = Path(__file__).parent.parent / "books.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
            read_date TEXT NOT NULL
        )
    ''')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_id ON books(user_id)')
    conn.commit()
    conn.close()

def add_book(title: str, author: str, rating: int, user_id: int):
    if not (1 <= rating <= 5):
        raise ValueError("Оценка должна быть от 1 до 5")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    today = date.today().isoformat()
    cursor.execute(
        'INSERT INTO books (user_id, title, author, rating, read_date) VALUES (?, ?, ?, ?, ?)',
        (user_id, title.strip(), author.strip(), rating, today)
    )
    conn.commit()
    conn.close()

def get_all_years(user_id: int) -> list[str]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT DISTINCT strftime("%Y", read_date)
        FROM books
        WHERE user_id = ?
        ORDER BY read_date DESC
    ''', (user_id,))
    years = [row[0] for row in cursor.fetchall()]
    conn.close()
    return years

def get_books_by_year(user_id: int, year: str) -> list[tuple]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT title, author, rating, read_date
        FROM books
        WHERE user_id = ? AND strftime("%Y", read_date) = ?
        ORDER BY read_date ASC
    ''', (user_id, year,))
    books = cursor.fetchall()
    conn.close()
    return books

def get_books_count_by_year(user_id: int) -> list[tuple]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT strftime("%Y", read_date) AS year, COUNT(*) AS count
        FROM books
        WHERE user_id = ?
        GROUP BY year
        ORDER BY year DESC
    ''', (user_id,))
    result = cursor.fetchall()
    conn.close()
    return result

def delete_book_by_user_and_date(user_id: int, title: str, author: str, read_date: str):
    """Удаляет конкретную книгу по совпадению всех полей."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        DELETE FROM books
        WHERE user_id = ? AND title = ? AND author = ? AND read_date = ?
    ''', (user_id, title, author, read_date))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted