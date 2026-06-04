from typing import List, Dict
from src.domain.entities import Note
from src.application.interfaces import NoteRepository


class InMemoryNoteRepository(NoteRepository):
    """
    Конкретная реализация хранилища.
    Она знает, что данные лежат в словаре (Dict).
    """

    def __init__(self):
        # Структура базы: { user_id: [Note, Note, ...] }
        self._storage: Dict[int, List[Note]] = {}
        self._current_id = 1

    async def save(self, note: Note) -> None:
        # Имитируем автоинкремент ID базы данных
        note.id = self._current_id
        self._current_id += 1

        if note.user_id not in self._storage:
            self._storage[note.user_id] = []

        self._storage[note.user_id].append(note)

    async def get_by_user(self, user_id: int) -> List[Note]:
        # Возвращаем список заметок или пустой список
        return self._storage.get(user_id, [])

    async def delete(self, note_id: int) -> None:
        for notes_list in self._storage.values():
            for note in notes_list:
                if note.id == note_id:
                    notes_list.remove(note)
                    return

    async def update(self, note_id: int, new_text: str) -> None:
        for notes_list in self._storage.values():
            for note in notes_list:
                if note.id == note_id:
                    note.text = new_text
                    return