# Файл: src/application/use_cases.py

from typing import List
from datetime import datetime
from src.domain.entities import Note
from src.application.interfaces import NoteRepository


class SaveNoteUseCase:
    """Сценарий: Сохранить новую заметку"""

    # Внедрение зависимости (Dependency Injection)
    def __init__(self, repo: NoteRepository):
        self.repo = repo

    async def execute(self, user_id: int, text: str) -> Note:
        # 1. Создаем доменную сущность
        note = Note(
            id=0,  # Настоящий ID выдаст база
            user_id=user_id,
            text=text,
            created_at=datetime.now()
        )

        # 2. Отправляем в хранилище через абстрактный интерфейс
        await self.repo.save(note)
        return note


class GetUserNotesUseCase:
    """Сценарий: Получить все заметки пользователя"""

    def __init__(self, repo: NoteRepository):
        self.repo = repo

    async def execute(self, user_id: int) -> List[Note]:
        # Просто делегируем запрос хранилищу
        return await self.repo.get_by_user(user_id)


class DeleteNoteUseCase:
    """Сценарий: Удалить заметку"""

    def __init__(self, repo: NoteRepository):
        self.repo = repo

    async def execute(self, note_id: int) -> None:
        await self.repo.delete(note_id)


class EditNoteUseCase:
    """Сценарий: Изменить заметку"""

    def __init__(self, repo: NoteRepository):
        self.repo = repo

    async def execute(self, note_id: int, new_text: str) -> None:
        await self.repo.update(note_id, new_text)