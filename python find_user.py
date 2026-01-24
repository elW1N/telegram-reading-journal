import sqlite3

def find_user_by_id(user_id: int):
    try:
        conn = sqlite3.connect('books.db')  # или ваше имя файла БД
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, username, first_name FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        return row
    except Exception as e:
        print(f"Ошибка: {e}")
        return None

if __name__ == "__main__":
    target_id = 4412233
    user = find_user_by_id(target_id)
    if user:
        print(f"Найден пользователь:\nID: {user[0]}\nUsername: {user[1] or 'нет'}\nИмя: {user[2]}")
    else:
        print(f"Пользователь с ID {target_id} не найден в базе.")