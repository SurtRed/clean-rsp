import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

# Импортируем нашу функцию загрузки конфига из папки core
from core.config import Config, load_config

# Настраиваем логирование, чтобы видеть в консоли, что происходит
logging.basicConfig(
    level=logging.INFO,
    format='%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    logger.info('Starting bot')

    # 1. Загружаем конфиг из файла.env
    config: Config = load_config()

    # 2. Инициализируем бот и диспетчер
    bot = Bot(
        token=config.tg_bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    # 3. Инициализируем диспетчер (главный маршрутизатор бота)
    dp = Dispatcher(maintenance_mode=False)

    # 4. Пропускаем старые апдейты, чтобы бот не отвечал на старые сообщения при запуске
    await bot.delete_webhook(drop_pending_updates=True)

    # 5. Запускаем бота в режиме long-polling
    await dp.start_polling(bot)

if __name__ == '__main__':
    # Запускаем асинхронную функцию main
    asyncio.run(main())

