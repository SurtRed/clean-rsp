import asyncio
import logging
import asyncpg
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from src.adapters.bot_handlers.note_handlers import note_handler_router
from src.adapters.bot_handlers.commands import commands_router
from src.infrastructure.postgres_repo import PostgresNoteRepository
from src.infrastructure.middlewares import DIMiddleware

# Импортируем нашу функцию загрузки конфига из папки core
from src.infrastructure.config import Config, load_config

# Настраиваем логирование, чтобы видеть в консоли, что происходит
logging.basicConfig(
    level=logging.INFO,
    format='%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    logger.info('Starting bot')

    # a. ИНФРАСТРУКТУРА: Создаем реальное хранилище

    # b. APPLICATION: Собираем сценарии, отдавая им хранилище
    # save_note_uc = SaveNoteUseCase(repo)
    # get_notes_uc = GetUserNotesUseCase(repo)
    # delete_note_uc = DeleteNoteUseCase(repo)

    # 1. Загружаем конфиг из файла.env
    config: Config = load_config()

    pool = await asyncpg.create_pool(
        host=config.db.host,
        port=config.db.port,
        user=config.db.user,
        password=config.db.password,
        database=config.db.database
    )

    repo = PostgresNoteRepository(pool)

    # 2. Инициализируем бот и диспетчер
    bot = Bot(
        token=config.tg_bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    # 3. Инициализируем диспетчер (главный маршрутизатор бота)
    dp = Dispatcher(maintenance_mode=False, storage=MemoryStorage())
    dp.update.middleware(DIMiddleware(repo))
    dp.include_router(commands_router)
    dp.include_router(note_handler_router)

    # 4. Пропускаем старые апдейты, чтобы бот не отвечал на старые сообщения при запуске
    await bot.delete_webhook(drop_pending_updates=True)

    # 5. Запускаем бота в режиме long-polling
    try:
        await dp.start_polling(bot)
    finally:
        await pool.close()
        logger.info('Pool closed')


if __name__ == '__main__':
    # Запускаем асинхронную функцию main
    asyncio.run(main())

