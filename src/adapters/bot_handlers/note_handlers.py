# Файл: src/adapters/bot_handlers/note_handlers.py

from aiogram import Router, types
from aiogram.filters import Command
from src.application.use_cases import SaveNoteUseCase, GetUserNotesUseCase

# Это наш Primary Adapter
router = Router()


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет! Напиши любой текст, и я сохраню его как заметку. А по команде /notes покажу список.")


@router.message(Command("notes"))
async def get_notes(message: types.Message, get_notes_use_case: GetUserNotesUseCase):
    # Хендлер ничего не знает про базу данных. Он просто просит Use Case дать заметки.
    notes = get_notes_use_case.execute(user_id=message.from_user.id)

    if not notes:
        await message.answer("У тебя пока нет заметок.")
        return

    # Формируем красивый ответ
    text = "\n".join([f"- {note.text}" for note in notes])
    await message.answer(f"Твои заметки:\n{text}")


@router.message()
async def save_note(message: types.Message, save_note_use_case: SaveNoteUseCase):
    # Извлекаем нужные данные из объекта Telegram и передаем в бизнес-логику
    save_note_use_case.execute(user_id=message.from_user.id, text=message.text)

    await message.answer("✅ Заметка сохранена!")