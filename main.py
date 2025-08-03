# main.py
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from config import TOKEN, ADMIN_IDS
from handlers import user, admin

async def set_default_commands(bot: Bot):
    """Устанавливаем базовые команды для всех пользователей"""
    commands = [
        BotCommand(command="start", description="Начать работу с ботом"),
        BotCommand(command="register", description="Зарегистрировать команду"),
        BotCommand(command="rating", description="Посмотреть рейтинг"),
        BotCommand(command="help", description="Список команд"),
    ]
    await bot.set_my_commands(commands)

async def set_admin_commands(bot: Bot, admin_id: int):
    """Устанавливаем команды для администратора"""
    admin_commands = [
        BotCommand(command="startgame", description="Запустить игру"),
        BotCommand(command="stopgame", description="Остановить игру"),
        BotCommand(command="resetgame", description="Сбросить игру"),
        BotCommand(command="broadcast", description="Сделать рассылку"),
        BotCommand(command="changeleader", description="Сменить лидера"),
        BotCommand(command="help", description="Список команд"),
    ]
    await bot.set_my_commands(admin_commands, scope={"type": "chat", "chat_id": admin_id})

async def main():
    bot = Bot(token=TOKEN)
    dp = Dispatcher()

    # ✅ Устанавливаем базовые команды для всех пользователей
    await set_default_commands(bot)

    # ✅ Регистрируем роутеры
    dp.include_router(admin.router)
    dp.include_router(user.router)

    print("✅ Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
