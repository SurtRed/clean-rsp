# DEV_JOURNAL — CleanRSP

Личный дневник разработки. Здесь — предпосылки, концепты, план и инструкции по развёртыванию.

---

## Предпосылки

Первый RSP-бот был написан на aiogram с нуля и без ИИ, на большом энтузиазме. Из-за больших
перерывов между сессиями разработки приходилось каждый раз вспоминать синтаксис Python,
паттерны asyncio, нюансы aiogram — почти с нуля. Тем не менее проект был доведён примерно
до 95% готовности и почти был готов к переезду на VPS.

Однако с ростом функционала стало очевидно: архитектура не масштабируется. В проекте
не было баз данных, не было строгого разделения ответственности. Путь апдейтов от Telegram
до обработчика становился всё труднее отследить из-за разветвлённых и местами циклических
импортов. Добавление нового функционала требовало всё больших усилий.

**Решение** — начать заново, исправив прошлые ошибки: применить концепт чистой архитектуры
и подключить базы данных. Разработка ведётся совместно с ИИ (Claude), что позволяет
поддерживать контекст между сессиями и изучать новые паттерны по ходу реализации.

**Цели:**
1. Самообразование — освоить Clean Architecture для применения в будущих проектах.
2. RSP-бот как учебный кейс: охватывает широкий арсенал возможностей Telegram (inline mode,
   FSM, inline keyboards, мультиплеер, shared state) — отличная точка входа в профессиональную
   разработку ботов.
3. Production — бот планируется к размещению на VPS для реального использования.

---

## Концепция Чистой Архитектуры

### Что это и зачем

Чистая архитектура (Clean Architecture, Robert C. Martin) — способ организации кода,
при котором бизнес-логика полностью изолирована от технических деталей (фреймворков,
баз данных, UI). Изменение технической реализации (например, смена PostgreSQL на Redis)
не затрагивает логику игры.

Главный принцип: **зависимости направлены строго внутрь**. Внешние слои знают о внутренних,
но не наоборот.

### 4 слоя (от центра к периферии)

```
┌──────────────────────────────────────────────────────────────────┐
│  adapters/   — «что пользователь видит и нажимает»               │
│  aiogram роутеры, inline keyboards, lexicon, FSM                 │
│                                                                  │
│    ┌──────────────────────────────────────────────────────────┐  │
│    │  infrastructure/  — «как хранятся и передаются данные»   │  │
│    │  реализации Repository, middleware, config, DB-clients   │  │
│    │                                                          │  │
│    │    ┌──────────────────────────────────────────────────┐  │  │
│    │    │  application/  — «что умеет делать система»      │  │  │
│    │    │  Use Cases, Repository Protocols (интерфейсы)    │  │  │
│    │    │                                                  │  │  │
│    │    │    ┌──────────────────────────────────────────┐  │  │  │
│    │    │    │  domain/  — «что такое объекты системы»  │  │  │  │
│    │    │    │  dataclasses, enums, чистая логика        │  │  │  │
│    │    │    └──────────────────────────────────────────┘  │  │  │
│    │    └──────────────────────────────────────────────────┘  │  │
│    └──────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

### Глоссарий

**Entity (Доменная сущность)**
Объект бизнес-логики: `Room`, `Player`, `RoundResult`. Представлен как Python dataclass
или enum. Не знает ни об aiogram, ни о базах данных.

**Use Case (Сценарий)**
Одна операция системы: `CreateRoomUseCase`, `MakeMoveUseCase`. Содержит метод `execute()`.
Знает только об интерфейсах (Protocol), не о конкретных реализациях.

**Repository (Репозиторий)**
Абстракция над хранилищем данных. В Python реализуется как `Protocol` — набор методов
без конкретной реализации. Use case работает с Protocol, не зная, лежит ли за ним dict,
Redis или PostgreSQL.

**Protocol (Интерфейс)**
Python-механизм для описания контракта (structural subtyping). Если класс реализует все
методы Protocol — он считается совместимым, без явного наследования.

**Adapter (Адаптер)**
Переводчик между внешним миром и бизнес-логикой. В нашем случае — aiogram-хендлеры.
Получают апдейт от Telegram, извлекают данные, вызывают use case, возвращают ответ.

**Dependency Inversion (Инверсия зависимостей)**
Use case зависит от абстракции (Protocol), а не от конкретного класса. Конкретный класс
(InMemoryRoomRepository или RedisRoomRepository) передаётся снаружи — и use case не знает,
что именно он получил.

**Dependency Injection (Внедрение зависимостей)**
Практический механизм инверсии зависимостей: конкретные объекты (репозитории, use cases)
создаются в точке входа (`main.py`) и передаются в хендлеры через middleware. Хендлер
не создаёт зависимости сам — он их получает готовыми.

**Middleware (в aiogram)**
Перехватчик, выполняющийся до (и после) каждого хендлера. `DIMiddleware` создаёт экземпляры
use cases и кладёт их в словарь `data`, откуда хендлер их забирает как аргументы функции.

**Inside-out разработка**
Подход «от центра к периферии»: сначала domain → application → infrastructure → adapters.
Каждый новый слой опирается на уже написанный и проверенный внутренний.

---

## План разработки

### Phase 1 — Note-бот (учебный прототип) ✅ ЗАВЕРШЕНА

Цель: освоить структуру чистой архитектуры на простом примере (CRUD заметок).

- Echo-бот на aiogram с полной структурой слоёв
- Domain entity: `Note` (dataclass)
- `NoteRepository` Protocol с методами: `save`, `get_by_user`, `delete`, `update`
- Use Cases: `SaveNoteUseCase`, `GetUserNotesUseCase`, `DeleteNoteUseCase`, `EditNoteUseCase`
- `InMemoryNoteRepository` (dict-based, данные в памяти процесса)
- `DIMiddleware` — инжектирует все Note use cases в хендлеры
- Команды: `/start`, `/help`, `/add`, `/list`, `/delete`, `/edit`
- Inline keyboard кнопки для выбора заметок
- FSM (Finite State Machine) для пошагового ввода текста
- Лексикон (`lexicon.py`) — все строки ответов вынесены отдельно

*Весь код Phase 1 закомментирован в актуальных файлах как учебный reference.*

---

### Phase 2 — PostgreSQL (персистентность данных) ✅ ЗАВЕРШЕНА

Цель: заменить InMemory хранилище на реальную базу без изменения хендлеров.

- `PostgresNoteRepository` — реализует `NoteRepository` через raw SQL + asyncpg
- Замена `InMemoryNoteRepository` на `PostgresNoteRepository` только в `main.py`
- Docker Compose: `postgres:16` (порт 5432) + Adminer (порт 8080) для просмотра БД
- Конфиг через `.env` файл: `BOT_TOKEN`, `POSTGRES_*`
- `Config` dataclass + `load_config()` через environs
- Данные переживают перезапуск бота — заметки сохраняются в PostgreSQL

---

### Phase 3 — RSP Game Bot ← ТЕКУЩАЯ ФАЗА

Цель: мультиплеерная игра «Камень-Ножницы-Бумага» с inline mode и persistence.

#### Phase 3.1 — Доменный и прикладной слои ✅ ЗАВЕРШЕНА

- **Domain entities** (все в `src/domain/entities.py`):
  - `Move` — enum: `ROCK`, `SCISSORS`, `PAPER`
  - `GameMode` — enum: `BEST_OF_1` (1 победа), `BEST_OF_3` (2 победы), `BEST_OF_5` (3 победы),
    `UNLIMITED` (= None, без автоматического завершения)
  - `RoomStatus` — enum: `WAITING`, `IN_PROGRESS`, `FINISHED`
  - `Player` — dataclass: `user_id: int`, `username: str`
  - `RoundResult` — dataclass с classmethod `from_moves()` — логика победителя инкапсулирована в домене
  - `Room` — dataclass: `room_id`, `mode`, `player1`, `created_at`, `status`, `current_round`,
    `player2`, `inline_message_id`, `rounds`
- **RoomRepository Protocol** (`src/application/interfaces.py`):
  - `create_room(room)`, `get_room(room_id)`, `save_room(room)`, `delete_room(room_id)`
- **Use Cases** (`src/application/use_cases.py`):
  - `CreateRoomUseCase` — создаёт `Room` и сохраняет через репозиторий
  - `JoinRoomUseCase` — добавляет второго игрока, переводит статус в `IN_PROGRESS`
  - `MakeMoveUseCase` — обрабатывает ход игрока, определяет конец раунда/игры
  - `CancelRoomUseCase` — удаляет комнату
- **InMemoryRoomRepository** (`src/infrastructure/memory_room_repo.py`): `dict[str, Room]`

#### Phase 3.2 — Основной игровой flow (handlers) ← СЛЕДУЮЩИЙ ШАГ

- `GameDIMiddleware` в `middlewares.py` — инжектирует RSP use cases
- Обновить `main.py`: убрать Note infrastructure, подключить InMemoryRoomRepository + GameDIMiddleware
- `src/adapters/bot_handlers/game_handlers.py` — хендлеры игры:
  - `/play` — предложить выбор режима (BEST_OF_1 / BEST_OF_3 / BEST_OF_5 / UNLIMITED)
  - Callback: выбор режима → CreateRoomUseCase → отправить invite-сообщение со ссылкой на комнату
  - Callback: вступить в комнату → JoinRoomUseCase → начать игру
  - Callback: ход (🪨 / ✂️ / 📄) → MakeMoveUseCase → показать результат раунда / конец игры
  - `/cancel` — CancelRoomUseCase
- `src/adapters/keyboards/game_keyboards.py` — inline клавиатуры для режима и хода
- Lexicon-записи для всех игровых сообщений

#### Phase 3.3 — Inline mode

Telegram inline mode позволяет начать игру прямо из любого чата, без перехода в бот.

- `InlineQueryHandler` — отвечает на inline-запрос, формирует invite
- `ChosenInlineResultHandler` — отслеживает `inline_message_id` для последующего редактирования
- Редактирование inline-сообщений через `bot.edit_message_text(inline_message_id=...)`
  вместо обычного `message.edit_text()`
- `room_id` для inline комнат: UUID (не `chat_id_message_id`)

#### Phase 3.4 — Redis (активный стейт игры)

- Добавить `redis` и `redis.asyncio` в зависимости
- `RedisRoomRepository` — реализует `RoomRepository`:
  - Хранит полные `Room`-объекты (сериализация через dataclasses_json или pickle)
  - TTL для автоудаления брошенных комнат
- Переключение `main.py`: `InMemoryRoomRepository` → `RedisRoomRepository`
- Хендлеры не меняются — только `main.py` и `middlewares.py`
- Docker Compose: добавить сервис `redis:7`

#### Phase 3.5 — PostgreSQL (история матчей и рейтинги)

- Схема БД: таблицы `rooms`, `players`, `match_results`, `pairwise_scores`
- Событие завершения игры (`RoomStatus.FINISHED`) → запись в PostgreSQL
- `/stats` команда — просмотр статистики игрока
- Рейтинги по парным матчам

---

### Phase 4 — Другой игровой бот

Детали TBD. Применение накопленного опыта Clean Architecture + Telegram на новом проекте.

---

### Phase 5 — Бизнес / CRM проект

Детали TBD. Переход от развлекательных к прикладным ботам.

---

## Восстановление воркфлоу

### Необходимый софт

| Инструмент | Версия / Ссылка | Примечание |
|---|---|---|
| Python | **3.14t** (free-threading / NoGIL) | Скачать с python.org — именно `3.14t`, не обычный `3.14` |
| PyCharm | 2026.2.1 | Professional или Community |
| Git for Windows | последний стабильный | Установить с bash-интерпретатором, добавить в PATH |
| Docker Desktop | последний стабильный | Нужен для Phase 2+ (PostgreSQL, Redis) |

AI-ассистент встроен в PyCharm и работает через Claude API — отдельная установка не нужна.

### 1. Git и bash

Установить Git for Windows. В процессе установки:
- Отметить галочку «Git Bash» (bash-интерпретатор)
- Добавить Git в PATH (опция «Git from the command line and also from 3rd-party software»)

После установки настроить локали bash — создать два файла в домашней директории (`~`):

**`~/.inputrc`:**
```
set meta-flag on
set input-meta on
set output-meta on
set convert-meta off
```

**`~/.bashrc`:**
```bash
export LANG=en_US.UTF-8
export LC_CTYPE=ru_RU.UTF-8
export LC_COLLATE=ru_RU.UTF-8
export PYTHONIOENCODING=utf-8
```

В PyCharm: Settings → Tools → Terminal → Shell path → указать путь к `bash.exe`
(обычно `C:\Program Files\Git\bin\bash.exe`).

### 2. Глобальная конфигурация Git

```bash
git config --global user.name "Твой ник"
git config --global user.email "email@domain.com"
git config --global core.autocrlf true
git config --global init.defaultBranch main

# Удобные алиасы для просмотра истории
git config --global alias.slog "log --graph --oneline --decorate --all"
git config --global alias.tree "log --graph --abbrev-commit --decorate --format=format:'%C(bold blue)%h%C(reset) - %C(bold green)(%ar)%C(reset) %C(white)%s%C(reset) %C(dim white)- %an%C(reset)%C(bold yellow)%d%C(reset)' --all"
```

Проверить:
```bash
git config --list
```

### 3. SSH-ключ для GitHub

Сгенерировать ключ и добавить на GitHub по инструкции:
https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent

Проверить соединение:
```bash
ssh -T git@github.com
```

### 4. Клонировать репозиторий

```bash
git clone git@github.com:SurtRed/CleanRSP.git
cd CleanRSP
```

### 5. Python 3.14t — создать виртуальное окружение

Убедиться, что установлен именно free-threading интерпретатор:
```bash
python3.14t --version
```

Создать виртуальное окружение (название `.venvt` — `t` означает free-threading):
```bash
python3.14t -m venv .venvt
```

Активировать (в bash):
```bash
source .venvt/Scripts/activate
```

Обновить pip:
```bash
python -m pip install --upgrade pip
```

Установить зависимости:
```bash
pip install -r requirements.txt
```

### 6. Настройка PyCharm

1. File → Settings → Project → Python Interpreter
2. Удалить преднастроенный интерпретатор
3. Добавить существующий: `.venvt/Scripts/python.exe` (путь относительно корня проекта)
4. Settings → Tools → Terminal → Shell path → `bash.exe` (путь из шага 1)

### 7. Файл переменных окружения

```bash
cp .env.example .env
```

Открыть `.env` и заполнить:
- `BOT_TOKEN` — токен бота от @BotFather в Telegram
- `POSTGRES_*` — параметры подключения к PostgreSQL (нужны начиная с Phase 2)

### 8. Docker (для Phase 2+)

Убедиться, что Docker Desktop запущен. Запустить базы данных:
```bash
docker compose up -d
```

Это поднимет:
- PostgreSQL 16 на порту `5432`
- Adminer (веб-интерфейс БД) на `http://localhost:8080`

### 9. Запуск бота

```bash
python main.py
```

### 10. Serena MCP (если доступен)

Serena — MCP-сервер для семантической навигации по коду (поиск символов, rename, type hierarchy).
Настраивается в настройках PyCharm: Settings → Tools → AI Assistant → Model Context Protocol (MCP).
После настройки — в первом сообщении новой сессии попросить Claude вызвать
`mcp__serena__activate_project` с путём к корню проекта.

Если Serena недоступна — весь необходимый контекст содержится в `CLAUDE.md`
(попросить Claude прочитать его в начале сессии: «прочитай CLAUDE.md»).

---

*Обновлено: 2026-06-14*
