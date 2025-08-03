# handlers/admin.py
from aiogram import Router, types, Bot
from aiogram.filters import Command
from config import ADMIN_IDS, ADMIN_PASSWORD, SPEED_BONUSES
from excel_utils import get_participants, add_bonus, set_end_time, freeze_leader, change_leader, update_status, reset_game
from handlers.user import send_question
from state_manager import init_player_state, active_states

router = Router()


@router.message(Command("setadmin"))
async def cmd_setadmin(message: types.Message, bot: Bot):
    args = message.text.split()
    if len(args) < 2 or args[1] != ADMIN_PASSWORD:
        await message.answer("❌ Неверный пароль.")
        return
    ADMIN_IDS.add(message.from_user.id)
    await set_admin_commands(bot, message.from_user.id)  # ✅ Добавляем админ-команды
    await message.answer("✅ Вы теперь админ. Команды обновлены.")

@router.message(Command("startgame"))
async def cmd_startgame(message: types.Message, bot: Bot):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("Нет прав.")
        return
    participants = get_participants()
    for p in participants:
        user_id = p[1]
        init_player_state(user_id)
        update_status(user_id, 1)
        await send_question(bot, user_id, 1)
    await message.answer("✅ Игра началась! Всем отправлен первый вопрос.")

@router.message(Command("stopgame"))
async def cmd_stopgame(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("Нет прав.")
        return
    participants = get_participants()
    for p in participants:
        if p[6] == "":
            set_end_time(p[1])
    completed = [p for p in participants if p[6] != ""]
    completed.sort(key=lambda x: x[6])
    for idx, team in enumerate(completed[:3]):
        add_bonus(team[1], SPEED_BONUSES[idx])
    await message.answer("✅ Квест завершён. Бонусы начислены!")

@router.message(Command("changeleader"))
async def cmd_changeleader(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("Нет прав.")
        return
    args = message.text.split()
    if len(args) != 3:
        await message.answer("Использование: /changeleader old_id new_id")
        return
    old_id, new_id = args[1], args[2]
    freeze_leader(old_id)
    change_leader(old_id, new_id, "новый_юзер")
    await message.answer("✅ Лидер изменён.")

@router.message(Command("broadcast"))
async def cmd_broadcast(message: types.Message, bot: Bot):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("Нет прав.")
        return
    text = message.text.replace("/broadcast", "").strip()
    participants = get_participants()
    for p in participants:
        try:
            await bot.send_message(chat_id=p[1], text=text)
        except:
            continue
    await message.answer("✅ Сообщение отправлено всем.")

# ✅ Новая команда: сброс игры
@router.message(Command("resetgame"))
async def cmd_resetgame(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("Нет прав.")
        return
    reset_game()
    active_states.clear()
    await message.answer("✅ Игра сброшена. Все участники удалены, состояния очищены.")
