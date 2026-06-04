from typing import List, Protocol
from src.domain.entities import Note

class NoteRepository(Protocol):
    """
        Это просто контракт. Здесь нет логики сохранения.
        Мы просто заявляем, какие методы должны быть у хранилища.
        """

    async def save(self, note: Note) -> None:
        pass

    async def get_by_user(self, user_id: int) -> List[Note]:
        pass

    async def delete(self, note_id: int) -> None:
        pass

    async def update(self, note_id: int, new_text: str) -> None:
        pass