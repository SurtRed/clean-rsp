# Файл: src/application/use_cases.py

from datetime import datetime
from src.domain.entities import Room, Player, Move, RoundResult, GameMode, RoomStatus
from src.application.interfaces import RoomRepository


# from src.domain.entities import Note
# from src.application.interfaces import NoteRepository


# class SaveNoteUseCase:
#     """Сценарий: Сохранить новую заметку"""
#
#     # Внедрение зависимости (Dependency Injection)
#     def __init__(self, repo: NoteRepository):
#         self.repo = repo
#
#     async def execute(self, user_id: int, text: str) -> Note:
#         # 1. Создаем доменную сущность
#         note = Note(
#             id=0,  # Настоящий ID выдаст база
#             user_id=user_id,
#             text=text,
#             created_at=datetime.now()
#         )
#
#         # 2. Отправляем в хранилище через абстрактный интерфейс
#         await self.repo.save(note)
#         return note
#
#
# class GetUserNotesUseCase:
#     """Сценарий: Получить все заметки пользователя"""
#
#     def __init__(self, repo: NoteRepository):
#         self.repo = repo
#
#     async def execute(self, user_id: int) -> List[Note]:
#         # Просто делегируем запрос хранилищу
#         return await self.repo.get_by_user(user_id)
#
#
# class DeleteNoteUseCase:
#     """Сценарий: Удалить заметку"""
#
#     def __init__(self, repo: NoteRepository):
#         self.repo = repo
#
#     async def execute(self, note_id: int) -> None:
#         await self.repo.delete(note_id)
#
#
# class EditNoteUseCase:
#     """Сценарий: Изменить заметку"""
#
#     def __init__(self, repo: NoteRepository):
#         self.repo = repo
#
#     async def execute(self, note_id: int, new_text: str) -> None:
#         await self.repo.update(note_id, new_text)

class CreateRoomUseCase:
    """Сценарий: рождение новой комнаты"""

    def __init__(self, repo: RoomRepository):
        self._repo = repo

    async def execute(self, room_id: str, mode: GameMode, player: Player, inline_message_id: str | None = None) -> Room:
        room = Room(
            room_id=room_id,
            mode=mode,
            player1=player,
            created_at=datetime.now(),
            inline_message_id=inline_message_id
        )
        await self._repo.create_room(room)
        return room

class JoinRoomUseCase:
    def __init__(self, repo: RoomRepository):
        self._repo = repo

    async def execute(self, room_id: str, player: Player) -> Room:
        room = await self._repo.get_room(room_id)
        if room is None:
            raise ValueError(f"Room {room_id} not found")
        if room.player2 is not None:
            raise ValueError("Room is already full")
        room.player2 = player
        room.status = RoomStatus.IN_PROGRESS
        await self._repo.save_room(room)
        return room

class MakeMoveUseCase:
    def __init__(self, repo: RoomRepository):
        self._repo = repo

    async def execute(self, room_id: str, user_id: int, move: Move) -> Room:
        room = await self._repo.get_room(room_id)
        if room is None:
            raise ValueError(f"Room {room_id} not found")

        p1_id = room.player1.user_id
        if room.player2 is None:
            raise ValueError("Second player has not joined yet")
        p2_id = room.player2.user_id

        if room.current_round is None:
            room.current_round = RoundResult(
                round_number=len(room.rounds) + 1,
                player1_move=move if user_id == p1_id else None,
                player2_move=move if user_id == p2_id else None,
                winner_id=None,
            )
        else:
            if user_id == p1_id:
                p1_move, p2_move = move, room.current_round.player2_move
            else:
                p1_move, p2_move = room.current_round.player1_move, move

            room.rounds.append(
                RoundResult.from_moves(
                    round_number=room.current_round.round_number,
                    p1_id=p1_id, p1_move=p1_move,
                    p2_id=p2_id, p2_move=p2_move,
                )
            )
            room.current_round = None

            wins_required = room.mode.wins_required
            if wins_required is not None:
                p1_wins = sum(1 for r in room.rounds if r.winner_id == p1_id)
                p2_wins = sum(1 for r in room.rounds if r.winner_id == p2_id)
                if p1_wins >= wins_required or p2_wins >= wins_required:
                    room.status = RoomStatus.FINISHED

        await self._repo.save_room(room)
        return room

class CancelRoomUseCase:
    def __init__(self, repo: RoomRepository):
        self._repo = repo

    async def execute(self, room_id: str) -> None:
        await self._repo.delete_room(room_id)