from aiogram import Router, F
from aiogram.types import Message

echo_router = Router()

@echo_router.message(F.text)
async def process_echo(message: Message):
    try:
        await message.send_copy(chat_id=message.chat.id)
    except TypeError:
        await message.answer("Я умею эхо-копировать только текст")