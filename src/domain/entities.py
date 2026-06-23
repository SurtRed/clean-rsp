from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

# @dataclass
# class Note:
#     id: int
#     user_id: int
#     text: str
#     created_at: datetime

class Move(Enum):
    ROCK = "rock"
    SCISSORS = "scissors"
    PAPER = "paper"


class GameMode(Enum):
    BEST_OF_1 = 1   # побеждает тот, кто выиграл 1 раунд
    BEST_OF_3 = 2   # побеждает тот, кто выиграл 2 раунда
    BEST_OF_5 = 3   # побеждает тот, кто выиграл 3 раунда
    UNLIMITED = None  # играют до тех пор, пока не остановятся вручную

    @property
    def wins_required(self) -> int | None:
        # для UNLIMITED возвращаем None — победитель не определяется автоматически
        if self.value is None:
            return None
        return self.value  # для остальных режимов value и есть нужное число побед

class RoomStatus(Enum):
    WAITING = "waiting"
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"

@dataclass
class Player:
    user_id: int
    username: str

@dataclass
class RoundResult:
    round_number: int
    player1_move: Move | None
    player2_move: Move | None
    winner_id: int | None

    @classmethod
    def from_moves(cls, round_number: int,
                   p1_id: int, p1_move: Move,
                   p2_id: int, p2_move: Move) -> "RoundResult":
        rules = {Move.ROCK: Move.SCISSORS, Move.SCISSORS: Move.PAPER, Move.PAPER: Move.ROCK}
        if p1_move == p2_move:
            winner_id = None
        elif rules[p1_move] == p2_move:
            winner_id = p1_id
        else:
            winner_id = p2_id
        return cls(round_number, p1_move, p2_move, winner_id)


@dataclass
class Room:
    room_id: str        #f"{chat_id}_{message_id}"
    mode: GameMode
    player1: Player
    created_at: datetime
    status: RoomStatus = RoomStatus.WAITING
    current_round: RoundResult | None = None  # None = раунд не начат
    player2: Player | None = None
    inline_message_id: str | None = None
    rounds: list[RoundResult] = field(default_factory=list)
