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

    def save(self, note: Note) -> None:
        # Имитируем автоинкремент ID базы данных
        note.id = self._current_id
        self._current_id += 1

        if note.user_id not in self._storage:
            self._storage[note.user_id] = []

        self._storage[note.user_id].append(note)

    def get_by_user(self, user_id: int) -> List[Note]:
        # Возвращаем список заметок или пустой список
        return self._storage.get(user_id, [])