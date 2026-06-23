# Файл: src/adapters/bot_handlers/commands.py
from aiogram import Router, types
from aiogram.filters import Command
from src.adapters.lexicon import LEXICON

# Это наш Primary Adapter
commands_router = Router()

@commands_router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(LEXICON["start"])

@commands_router.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(LEXICON["help"])


