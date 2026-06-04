from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def get_note_keyboard(note_id: int) -> InlineKeyboardMarkup:
    # Создаём кнопку: text — видит пользователь, callback_data — получит бот
    delete_button = InlineKeyboardButton(
        text="❌ Удалить",
        callback_data=f"delete_{note_id}"
    )
    edit_button = InlineKeyboardButton(
        text="✍️ Редактировать",
        callback_data=f"edit_{note_id}"
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[delete_button, edit_button]])
    return keyboard