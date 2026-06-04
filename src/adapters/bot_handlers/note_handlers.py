# Файл: src/adapters/bot_handlers/note_handlers.py

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from src.adapters.states.note_states import NoteEdit
from src.application.use_cases import SaveNoteUseCase, GetUserNotesUseCase, DeleteNoteUseCase, EditNoteUseCase
from src.adapters.lexicon import LEXICON
from src.adapters.keyboards.note_keyboards import get_note_keyboard

# Это наш Primary Adapter
note_handler_router = Router()

@note_handler_router.callback_query(F.data.startswith("delete_"))
async def delete_note(callback: types.CallbackQuery, delete_note_use_case: DeleteNoteUseCase):
    # Хендлер перехватывает нажатие кнопки и выполняет функцию удаления заметки
    data_id = int(callback.data.split("_")[1])
    await delete_note_use_case.execute(note_id=data_id)
    await callback.message.delete()
    await callback.answer(LEXICON["note_deleted"])

@note_handler_router.callback_query(F.data.startswith("edit_"))
async def edit_note(callback: types.CallbackQuery, state: FSMContext):
    # Хендлер перехватывает нажатие кнопки и предлагает пользователю написать новый текст
    await state.set_state(NoteEdit.waiting_for_new_text)
    data_id = int(callback.data.split("_")[1])
    await state.update_data(note_id=data_id)
    await callback.message.answer(LEXICON["awaited_new_text"])
    await callback.answer()

@note_handler_router.message(NoteEdit.waiting_for_new_text)
async def edited_note_text(message: types.Message, state: FSMContext, edit_note_use_case: EditNoteUseCase):
    # Хендлер принимает текст для редактирования заметки
    data = await state.get_data()
    note_id = data["note_id"]
    await edit_note_use_case.execute(note_id=note_id, new_text=message.text)
    await state.clear()
    await message.answer(LEXICON["note_updated"])

@note_handler_router.message(Command("notes"))
async def get_notes(message: types.Message, get_notes_use_case: GetUserNotesUseCase):
    # Хендлер ничего не знает про базу данных. Он просто просит Use Case дать заметки.
    notes = await get_notes_use_case.execute(user_id=message.from_user.id)

    if not notes:
        await message.answer(LEXICON["no_notes"])
        return

    # Формируем цикл ответов
    for note in notes:
        await message.answer(
            text=note.text,
            reply_markup=get_note_keyboard(note.id)
        )

    # text = "\n".join([f"- {note.text}" for note in notes])
    # await message.answer(LEXICON["notes_header"] + text)


@note_handler_router.message()
async def save_note(message: types.Message, save_note_use_case: SaveNoteUseCase):
    # Извлекаем нужные данные из объекта Telegram и передаем в бизнес-логику
    await save_note_use_case.execute(user_id=message.from_user.id, text=message.text)

    await message.answer(LEXICON["note_saved"])