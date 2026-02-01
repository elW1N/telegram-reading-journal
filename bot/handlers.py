from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

from db.database import get_books_count_by_year

def get_main_menu():
    """Возвращает клавиатуру главного меню."""
    keyboard = [
        ["Добавить книгу", "Список"],
        ["Статистика"]
    ]
    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=False
    )

async def back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик кнопки 'Назад'."""
    await update.message.reply_text(
        "Вы вернулись в главное меню.",
        reply_markup=get_main_menu()
    )
    return ConversationHandler.END

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # 🔍 Выводим user_id в логи (только для отладки!)
    user_id = update.effective_user.id
    print(f"✅ Твой user_id: {user_id}")

    # Создаём клавиатуру
    keyboard = [
        ["Добавить книгу", "Список"],
        ["Статистика"]
    ]
    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,      # подстраивает размер под экран
        one_time_keyboard=False     # клавиатура остаётся всегда
    )

    await update.message.reply_text(
        "Привет! Я читательский дневник.\n\n"
        "Выберите действие:",
        reply_markup=reply_markup
    )

async def show_statistics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    stats = get_books_count_by_year(user_id)
    if not stats:
        await update.message.reply_text("Вы ещё не добавили ни одной книги.")
        return

    message = "📊 Статистика чтения:\n\n"
    total = 0
    for year, count in stats:
        message += f"{year} год — {count} книг\n"
        total += count
    message += f"\nВсего прочитано: {total} книг"
    await update.message.reply_text(message)

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Действие отменено.")
    return ConversationHandler.END
