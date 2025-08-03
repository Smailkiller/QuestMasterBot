# main.py
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from config import TOKEN
from handlers import user, admin

# ✅ Функция для установки стандартных команд
async def set_default_commands(bot: Bot, user_id: int = None):
    commands = [
        BotCommand(command="start", description="Начать работу с ботом"),
        BotCommand(command="register", description="Зарегистрировать команду"),
        BotCommand(command="rating", description="Посмотреть рейтинг"),
        BotCommand(command="help", description="Список команд"),
    ]
    if user_id:
        await bot.set_my_commands(commands, scope={"type": "chat", "chat_id": user_id})
    else:
        await bot.set_my_commands(commands)

async def main():
    bot = Bot(token=TOKEN)
    dp = Dispatcher()

    # ✅ Устанавливаем команды по умолчанию для всех
    await set_default_commands(bot)

    # ✅ Регистрируем обработчики
    dp.include_router(user.router)
    dp.include_router(admin.router)

    print("✅ Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
