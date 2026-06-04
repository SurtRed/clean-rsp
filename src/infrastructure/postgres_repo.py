from typing import List
import asyncpg
from src.domain.entities import Note
from src.application.interfaces import NoteRepository


class PostgresNoteRepository(NoteRepository):

    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def save(self, note: Note) -> None:
        row = await self.pool.fetchrow(
            "INSERT INTO notes (user_id, text) VALUES ($1, $2) RETURNING id, created_at",
            note.user_id, note.text
        )
        note.id = row["id"]
        note.created_at = row["created_at"]

    async def get_by_user(self, user_id: int) -> List[Note]:
        rows = await self.pool.fetch(
            "SELECT id, user_id, text, created_at FROM notes WHERE user_id = $1 ORDER BY id",
            user_id
        )
        return [Note(id=r["id"], user_id=r["user_id"], text=r["text"], created_at=r["created_at"]) for r in rows]

    async def delete(self, note_id: int) -> None:
        await self.pool.execute(
            "DELETE FROM notes WHERE id = $1",
            note_id
        )

    async def update(self, note_id: int, new_text: str) -> None:
        await self.pool.execute(
            "UPDATE notes SET text = $1 WHERE id = $2",
            new_text, note_id
        )