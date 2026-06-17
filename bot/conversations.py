import re
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
    ConversationHandler,
    )

from constants import *
from db.database import get_books_by_year, get_all_years, add_book, delete_book_by_user_and_date
from bot.handlers import get_main_menu




async def start_add_book(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [["Отмена"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

    await update.message.reply_text(
        '📚 Введите полное имя автора (например: Михаил Булгаков):',
        reply_markup=reply_markup
    )
    return ADD_AUTHOR

async def handle_author(update: Update, context: ContextTypes.DEFAULT_TYPE):
    author = update.message.text.strip()
    if author.lower() == "отмена":
        return await cancel_adding(update, context)
    
    if not author or len(author) < 2:
        await update.message.reply_text('❌ Имя автора слишком короткое. Попробуйте снова:')
        return ADD_AUTHOR

    context.user_data['author'] = author
    
    keyboard = [["Отмена"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
    
    await update.message.reply_text(
        '📖 Введите название книги (без кавычек):',
        reply_markup=reply_markup
    )
    return ADD_TITLE

def format_title(title: str) -> str:
    """Форматирует название: первая буква заглавная, остальные — как есть."""
    title = title.strip()
    if not title:
        return title
    # Делаем первую букву заглавной, остальное — без изменений
    return title[0].upper() + title[1:]

async def handle_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if text.lower() == "отмена":
        return await cancel_adding(update, context)
    
    if not text or len(text) < 2:
        await update.message.reply_text('❌ Название слишком короткое. Попробуйте снова:')
        return ADD_TITLE

    formatted_title = format_title(text)
    context.user_data['title'] = formatted_title

    keyboard = [["Отмена"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

    await update.message.reply_text(
        '⭐ Оцените книгу от 1 до 5:',
        reply_markup=reply_markup
    )
    return ADD_RATING

async def handle_rating(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if text.lower() == "отмена":
        return await cancel_adding(update, context)
    
    try:
        rating = int(text)
    except ValueError:
        await update.message.reply_text('❌ Пожалуйста, введите число от 1 до 5.')
        return ADD_RATING

    if not (1 <= rating <= 5):
        await update.message.reply_text('❌ Оценка должна быть от 1 до 5.')
        return ADD_RATING

    context.user_data['rating'] = rating
    author = context.user_data['author']
    title = context.user_data['title']

    # Форматируем с «ёлочками»
    display_title = f'«{title}»'

    keyboard = [["Да", "Отмена"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

    await update.message.reply_text(
        f'Подтвердите запись:\n{author} {display_title} — {rating}/5',
        reply_markup=reply_markup
    )
    return ADD_CONFIRM

async def confirm_book(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if text.lower() in ("отмена", "нет"):
        return await cancel_adding(update, context)
    
    if text.lower() not in ("да", "yes"):
        await update.message.reply_text('Пожалуйста, нажмите «Да» или «Отмена».')
        return ADD_CONFIRM

    user_id = update.effective_user.id
    author = context.user_data['author']
    title = context.user_data['title']
    rating = context.user_data['rating']

    try:
        add_book(title, author, rating, user_id)
        await update.message.reply_text(
            f"✅ Книга сохранена!\n{author} «{title}» — {rating}/5",
            reply_markup=get_main_menu()
        )
    except Exception as e:
        await update.message.reply_text(
            "❌ Ошибка при сохранении.",
            reply_markup=get_main_menu()
        )
        print(f"DB Error: {e}")

    return ConversationHandler.END

async def cancel_adding(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❌ Добавление книги отменено.",
        reply_markup=get_main_menu()
    )
    return ConversationHandler.END


# === ДИАЛОГ: ПРОСМОТР КНИГ ===

async def start_view_books(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    years = get_all_years(user_id)
    if not years:
        await update.message.reply_text("Вы ещё не добавили ни одной книги.")
        return ConversationHandler.END
    
    keyboard = [["Назад"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    years_list = "\n".join(f"• {year}" for year in years)
    await update.message.reply_text(
        f'Доступные годы:\n{years_list}\n\nВведите год (например, 2025):',
        reply_markup=reply_markup
    )
    return VIEW_WAITING_FOR_YEAR

async def handle_selected_year(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    
    if not (text.isdigit() and len(text) == 4):
        await update.message.reply_text("Пожалуйста, введите год в формате YYYY (например, 2025).")
        return VIEW_WAITING_FOR_YEAR

    year = text
    books = get_books_by_year(user_id, year)

    if not books:
        await update.message.reply_text(f"В {year} году у вас нет прочитанных книг.\nВведите другой год:")
        return VIEW_WAITING_FOR_YEAR

    context.user_data['books_for_deletion'] = books
    context.user_data['year_for_deletion'] = year

    total = len(books)
    message = f"{year} год — {total} кн.\n\n"
    current_month = None
    book_number = 1

    for title, author, rating, read_date in books:
        month_num = int(read_date.split('-')[1])
        month_name = MONTHS_RU[month_num]

        if month_name != current_month:
            current_month = month_name
            message += f"📅 {current_month}\n"

        message += f"{book_number}. {author} — «{title}» — {rating}/5\n"
        book_number += 1

    if len(message) > 4000:
        message = message[:4000] + "\n... (список сокращён)"

    keyboard = [
        ["Назад", "Удалить книгу"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        message,
        reply_markup=reply_markup
    )
    return VIEW_WAITING_FOR_YEAR

async def handle_invalid_year_input(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ):
    await update.message.reply_text(
        "Пожалуйста, введите год в формате YYYY (например, 2025)."
    )
    return "WAITING_FOR_YEAR"

async def start_delete_from_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    books = context.user_data.get('books_for_deletion')
    if not books:
        await update.message.reply_text("Список книг недоступен. Попробуйте снова.")
        return VIEW_WAITING_FOR_YEAR

    message = "🗑️ Напишите номер книги для удаления:\n\n"
    for i, (title, author, rating, _) in enumerate(books, 1):
        message += f"{i}. {author} «{title}»\n"

    keyboard = [["Отмена"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(message, reply_markup=reply_markup)

    return DELETE_WAITING_FOR_NUMBER

async def handle_delete_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if text.lower() == "отмена":
        return await cancel_adding(update, context)

    try:
        index = int(text) - 1
        books = context.user_data['books_for_deletion']
        if index < 0 or index >= len(books):
            raise ValueError
        book = books[index]
        title, author, rating, read_date = book

        context.user_data['book_to_delete'] = book
        context.user_data['delete_index'] = index

        keyboard = [["Да", "Отмена"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

        await update.message.reply_text(
            f"Подтвердите удаление:\n{author} «{title}»",
            reply_markup=reply_markup
        )
        return DELETE_CONFIRM

    except (ValueError, IndexError):
        await update.message.reply_text("❌ Неверный номер. Введите число из списка:")
        return DELETE_WAITING_FOR_NUMBER

async def confirm_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if text.lower() in ("отмена", "нет"):
        return await cancel_adding(update, context)

    if text.lower() not in ("да", "yes"):
        await update.message.reply_text("Пожалуйста, нажмите «Да» или «Отмена».")
        return DELETE_CONFIRM

    user_id = update.effective_user.id
    book = context.user_data['book_to_delete']
    title, author, _, read_date = book

    success = delete_book_by_user_and_date(user_id, title, author, read_date)

    if success:
        await update.message.reply_text("✅ Книга удалена!", reply_markup=get_main_menu())
    else:
        await update.message.reply_text("❌ Не удалось найти книгу для удаления.", reply_markup=get_main_menu())

    return ConversationHandler.END
