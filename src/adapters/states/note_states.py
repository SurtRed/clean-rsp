from aiogram.fsm.state import State, StatesGroup

class NoteEdit(StatesGroup):
    waiting_for_new_text = State()