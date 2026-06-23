from typing import Protocol
from src.domain.entities import Room

# class NoteRepository(Protocol):
#     """
#         Это просто контракт. Здесь нет логики сохранения.
#         Мы просто заявляем, какие методы должны быть у хранилища.
#         """
#
#     async def save(self, note: Note) -> None:
#         pass
#
#     async def get_by_user(self, user_id: int) -> List[Note]:
#         pass
#
#     async def delete(self, note_id: int) -> None:
#         pass
#
#     async def update(self, note_id: int, new_text: str) -> None:
#         pass

class RoomRepository(Protocol):
    async def create_room(self, room: Room) -> None: ...
    async def get_room(self, room_id: str) -> Room | None: ...
    async def save_room(self, room: Room) -> None: ...
    async def delete_room(self, room_id: str) -> None: ...