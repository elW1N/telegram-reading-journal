import sqlite3
from datetime import date


def init_db():
    '''
    Docstring для init_bd
    '''
    conn = sqlite3.connect('books.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
            read_date TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def add_book(title: str, author: str, rating: int):
    if not(1 <= rating <= 5):
        raise ValueError('Оценка должна быть от 1 до 5')
    conn = sqlite3.connect('books.db')
    cursor = conn.cursor()
    today = date.today().isoformat()
    cursor.execute(
        'INSERT INTO books (title, author, rating, read_date) VALUES (?, ?, ?, ?)',
        (title.strip(), author.strip(), rating, today)
    )
    conn.commit()
    conn.close()

def get_all_years() -> list[str]:
    '''Возвращает список лет(в виде строк), за которое есть книги'''
    conn = sqlite3.connect('books.db')
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT strftime("%Y", read_date) FROM books ORDER BY read_date DESC')
    years = [row[0] for row in cursor.fetchall()]
    conn.close
    return years

def get_books_by_year(year: str) -> list[tuple]:
    """
    Возвращает книги за указанный год.
    Каждая книга: (title, author, rating, read_date)
    Сортировка: по дате (от старых к новым).
    """
    conn = sqlite3.connect('books.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT title, author, rating, read_date
        FROM books
        WHERE strftime("%Y", read_date) = ?
        ORDER BY read_date ASC
    ''', (year,))
    books = cursor.fetchall()
    conn.close()
    return books

def get_books_count_by_year() -> list[tuple]:
    """
    Возвращает список кортежей: (год, количество_книг)
    Отсортировано по году по убыванию.
    """
    conn = sqlite3.connect('books.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT strftime("%Y", read_date) AS year, COUNT(*) AS count
        FROM books
        GROUP BY year
        ORDER BY year DESC
    ''')
    result = cursor.fetchall()
    conn.close()
    return result
