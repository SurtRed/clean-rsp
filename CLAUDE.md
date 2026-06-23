# CleanRSP — Инструкции для Claude

## О проекте
Telegram-бот «Камень-Ножницы-Бумага» на чистой архитектуре.
Учебно-практический проект: цель — освоить Clean Architecture и довести до production (VPS).
Планируется реальное использование реальными пользователями.

## При старте каждой сессии
> Этот файл не загружается автоматически — разработка ведётся в PyCharm AI Agent (Claude API).
> Попросить Claude прочитать `CLAUDE.md` в начале сессии.

1. Прочитать этот файл (`CLAUDE.md`)
2. Вызвать `mcp__serena__initial_instructions`
3. Вызвать `mcp__serena__read_memory` для памяти: `architecture`, `roadmap`, `phase3/design`, `project-snapshot`
4. При необходимости полного контекста — прочитать `DEV_JOURNAL.md`

## Архитектурные слои

```
      ┌──────────────┐
      │  adapters/   │  aiogram роутеры, клавиатуры, lexicon
      └──────┬───────┘
             │ вызывает
      ┌──────▼─────────────┐
      │   application/     │  use cases, repository interfaces (Protocol)
      └──────┬─────────────┘
             │ импортирует
      ┌──────▼──────┐
      │   domain/   │  entity dataclasses, enums — без зависимостей
      └─────────────┘
             ↑
      ┌──────┴──────────────────┐
      │    infrastructure/      │  реализации хранилищ, middleware, config
      └─────────────────────────┘
```

Правило изоляции: каждый слой импортирует только внутренние слои.
`adapters/` не знает об `infrastructure/`. Use cases не знают об aiogram.

## Inside-out алгоритм (добавление фичи)
1. Объявить метод в `RoomRepository` Protocol → `interfaces.py`
2. Создать `XxxUseCase` с `execute()` → `use_cases.py`
3. Реализовать в `InMemoryRoomRepository` → `memory_room_repo.py`
4. Добавить use case в `GameDIMiddleware` → `middlewares.py`
5. Написать handler через DI → `game_handlers.py`

## Карта файлов

| Файл | Слой | Роль |
|------|------|------|
| `src/domain/entities.py` | domain | Move, GameMode, RoomStatus, Player, RoundResult, Room |
| `src/application/interfaces.py` | application | RoomRepository Protocol (4 метода) |
| `src/application/use_cases.py` | application | CreateRoom, JoinRoom, MakeMove, CancelRoom |
| `src/infrastructure/memory_room_repo.py` | infrastructure | InMemoryRoomRepository (dict-based, dev/test) |
| `src/infrastructure/middlewares.py` | infrastructure | DIMiddleware → **нужна GameDIMiddleware** |
| `src/infrastructure/config.py` | infrastructure | Config dataclass + load_config() |
| `src/adapters/bot_handlers/commands.py` | adapters | /start, /help |
| `src/adapters/lexicon.py` | adapters | строки ответов |
| `main.py` | — | точка входа, сборка зависимостей |

Файлы с `note_` в имени и закомментированный код в `interfaces.py`, `use_cases.py`,
`memory_room_repo.py`, `middlewares.py` — учебный reference Phase 1/2. Не удалять.

## Текущий статус (Phase 3, по состоянию на 2026-06-14)

| Файл | Статус |
|------|--------|
| `src/domain/entities.py` | ✅ готов |
| `src/application/interfaces.py` | ✅ RoomRepository Protocol |
| `src/application/use_cases.py` | ✅ CreateRoom, JoinRoom, MakeMove, CancelRoom |
| `src/infrastructure/memory_room_repo.py` | ✅ InMemoryRoomRepository |
| `src/infrastructure/middlewares.py` | 🔄 нужна GameDIMiddleware (RSP use cases) |
| `src/adapters/bot_handlers/game_handlers.py` | ⏳ не создан |
| `main.py` | ⏳ всё ещё импортирует Note infrastructure |

## Следующий шаг
Создать `GameDIMiddleware` в `src/infrastructure/middlewares.py` по образцу существующей
`DIMiddleware` (Phase 1/2 reference, там же закомментирована). Инжектировать:
`CreateRoomUseCase`, `JoinRoomUseCase`, `MakeMoveUseCase`, `CancelRoomUseCase`.

Затем создать `src/adapters/bot_handlers/game_handlers.py`.
Затем обновить `main.py` — заменить Note infrastructure на RSP.

## Ключевые архитектурные решения (не менять без обсуждения)
- `room_id = f"{chat_id}_{message_id}"` для обычных чатов; UUID для inline mode
- `inline_message_id: str | None` в `Room` — для редактирования inline-сообщений через Bot API
- `current_round: RoundResult | None` в `Room` — незавершённый раунд (один игрок сходил)
- `GameMode.UNLIMITED = None` + `@property wins_required → int | None`
- `RoundResult.from_moves()` — classmethod с rules-dict, вся логика победителя в домене
- `get_waiting_rooms` намеренно отложен — нужна эмпирическая проверка ChosenInlineResult
- `player1_move: Move | None` в RoundResult допускает частичное состояние — type checker может предупреждать, это сознательный компромисс

## Технический стек
- Python **3.14t** (free-threading / NoGIL) — venv: `.venvt`
- aiogram **3.28.2**
- asyncpg **0.31.0** (PostgreSQL)
- Redis — запланирован (Phase 3.4)
- OS: Windows 10, IDE: PyCharm 2026.2.1

## Соглашения кода
- Идентификаторы: английский; комментарии: русский
- Комментарии только к WHY, не к WHAT
- Старый Note-код: закомментировать, не удалять (учебный reference)
- Замена хранилища (InMemory → Redis → Postgres) — только в `main.py` и `middlewares.py`, handlers не трогать
- Пользователь изучает концепты пошагово — объяснять новые паттерны (Redis, async, etc.) по ходу реализации
