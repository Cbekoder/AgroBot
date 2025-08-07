from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram import html

from loader import dp

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    await message.answer(f"👋 Assalomu alaykum, {html.bold(message.from_user.full_name)}. Men AgroBotman.\n"
                         f"📸 Iltimos, o‘simlik rasmini yuboring va men uni tahlil qilib beraman!")
