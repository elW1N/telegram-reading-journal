import os
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler

from bot.handlers import start, show_statistics, cancel, back_to_menu

from bot.conversations import (
    start_add_book,
    handle_author,
    handle_title,
    handle_rating,
    confirm_book,
    start_view_books,
    handle_selected_year,
    handle_invalid_year_input,
    cancel_adding
)

# Константы состояний
from constants import (
    ADD_AUTHOR,
    ADD_TITLE,
    ADD_RATING,
    ADD_CONFIRM,
    VIEW_WAITING_FOR_YEAR
)

from db.database import init_db

load_dotenv()
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not TOKEN:
    raise ValueError('Токен не найден! Убедитесь, что он указан в файле .env')


def main():
    init_db()
    app = Application.builder().token(TOKEN).build()

    # ЕДИНЫЙ диалог для всех сценариев
    conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex(r'(?i)^добавить книгу$'), start_add_book),
            MessageHandler(filters.Regex(r'(?i)^список$'), start_view_books),
        ],
        states={
            # Добавление книги
            ADD_AUTHOR: [
                MessageHandler(filters.Regex(r'(?i)^отмена$'), cancel_adding),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_author)
            ],
            ADD_TITLE: [
                MessageHandler(filters.Regex(r'(?i)^отмена$'), cancel_adding),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_title)
            ],
            ADD_RATING: [
                MessageHandler(filters.Regex(r'(?i)^отмена$'), cancel_adding),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_rating)
            ],
            ADD_CONFIRM: [
                MessageHandler(filters.Regex(r'(?i)^отмена$'), cancel_adding),
                MessageHandler(filters.Regex(r'(?i)^(да|yes)$'), confirm_book)
            ],

            # Просмотр книг
            VIEW_WAITING_FOR_YEAR: [
                MessageHandler(filters.Regex(r'(?i)^назад$'), back_to_menu),
                MessageHandler(filters.Regex(r'^\d{4}$'), handle_selected_year),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_invalid_year_input)
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    # Основные обработчики
    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.Regex(r'(?i)^статистика$'), show_statistics))
    app.add_handler(conv_handler)

    app.run_polling()


if __name__ == '__main__':
    main()