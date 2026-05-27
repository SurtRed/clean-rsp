from typing import List, Protocol
from src.domain.entities import Note

class NoteRepository(Protocol):
    """
        Это просто контракт. Здесь нет логики сохранения.
        Мы просто заявляем, какие методы должны быть у хранилища.
        """

    def save(self, note: Note) -> None:
        pass

    def get_by_user(self, user_id: int) -> List[Note]:
        pass

