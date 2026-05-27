from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from src.application.interfaces import NoteRepository
from src.application.use_cases import SaveNoteUseCase, GetUserNotesUseCase


class DIMiddleware(BaseMiddleware):
    """
    Мидлварь для внедрения зависимостей (Dependency Injection).
    Она перехватывает каждое сообщение ДО того, как оно попадет в хендлер.
    """

    def __init__(self, repo: NoteRepository):
        self.repo = repo

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        # 1. ДО ХЕНДЛЕРА: Создаем свежие экземпляры UseCase для текущего апдейта
        # В будущем здесь ты будешь открывать транзакцию к PostgreSQL:
        # async with db_pool.acquire() as session:

        data["save_note_use_case"] = SaveNoteUseCase(self.repo)
        data["get_notes_use_case"] = GetUserNotesUseCase(self.repo)

        # 2. ПЕРЕДАЕМ УПРАВЛЕНИЕ: Отправляем апдейт дальше (в хендлер)
        # Хендлер получит всё, что мы только что положили в словарь `data`
        result = await handler(event, data)

        # 3. ПОСЛЕ ХЕНДЛЕРА: Очистка (выполнится после того, как бот ответит)
        # Здесь в будущем будет закрываться транзакция БД:
        # session.commit()
        # session.close()

        return result