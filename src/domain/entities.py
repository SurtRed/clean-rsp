from dataclasses import dataclass
from datetime import datetime

@dataclass
class Note:
    id: int
    user_id: int
    text: str
    created_at: datetime