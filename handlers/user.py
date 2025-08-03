from aiogram import Router, types, Bot, F
from aiogram.filters import Command
from excel_utils import (
    user_exists, add_participant, get_participants, get_quest_title,
    update_status, update_score, get_question_data,
    set_start_time, set_end_time, get_status
)
from config import excel_lock, SKIP_PENALTY, ADMIN_IDS
from keyboards import question_keyboard
from state_manager import (
    init_player_state, get_state, set_message_id,
    add_attempt, add_hint, active_states
)

router = Router()

# ✅ Хранилище для регистрации
waiting_for_team_name = set()

# ✅ /start
@router.message(Command("start"))
async def cmd_start(message: types.Message):
    if not user_exists(message.from_user.id):
        await message.answer("Привет! Вы ещё не зарегистрированы. Введите /register, чтобы присоединиться.")
    else:
        await message.answer("Вы уже зарегистрированы! Ждите начала игры.")

# ✅ /register
@router.message(Command("register"))
async def cmd_register(message: types.Message):
    if user_exists(message.from_user.id):
        await message.answer("Вы уже зарегистрированы! Название команды изменить нельзя.")
        return
    waiting_for_team_name.add(message.from_user.id)
    await message.answer("Введите название вашей команды (одно сообщение):")

# ✅ Обработка текста (название команды или ответ)
@router.message(F.text & ~F.text.startswith("/"))
async def handle_text(message: types.Message):
    user_id = message.from_user.id
    await message.delete()  # ✅ Удаляем сообщение игрока

    # ✅ Название команды
    if user_id in waiting_for_team_name:
        team_name = message.text.strip()
        if len(team_name) < 2:
            await message.answer("Название слишком короткое. Попробуйте снова:")
            return

        async with excel_lock:
            add_participant(user_id, message.from_user.username, team_name, status="wait")

        waiting_for_team_name.remove(user_id)
        await message.answer(f"✅ Команда '{team_name}' зарегистрирована! Ждите старта.")
        return

    # ✅ Проверка регистрации
    if not user_exists(user_id):
        await message.answer("Вы ещё не зарегистрированы. Введите /register.")
        return

    # ✅ Проверка статуса
    status = str(get_status(user_id))

    if status == "wait":
        await message.answer("Ожидайте начала квеста...")
        return
    elif status == "finished":
        await message.answer("Вы уже завершили квест! Ждите итогов.")
        return

    # ✅ Ответ на вопрос
    if status.isdigit() and int(status) >= 1:
        await process_answer(message)

# ✅ Обработка ответа
async def process_answer(message: types.Message):
    user_id = message.from_user.id
    status = int(get_status(user_id))
    answer = message.text.strip().lower()
    state = get_state(user_id)
    add_attempt(user_id, answer)

    q_data = get_question_data(status)

    if answer in q_data["answers"]:
        update_score(user_id, q_data["price"])

        # ✅ Обновляем сообщение
        await send_question(message.bot, user_id, status, "🟢 Ответ принят 🟢", state_update=False, disable_buttons=True)

        # ✅ Последний вопрос
        if status >= q_data["max_q"]:
            set_end_time(user_id)
            update_status(user_id, "finished")
            if user_id in active_states:
                del active_states[user_id]
            await message.bot.send_message(user_id, "🎉 Вы завершили квест! Спасибо за участие.")
            return

        # ✅ Следующий вопрос
        update_status(user_id, status + 1)
        init_player_state(user_id)
        await send_question(message.bot, user_id, status + 1, "")
    else:
        await send_question(message.bot, user_id, status, "🔴 Ответ не верный 🔴", state_update=False)

# ✅ /rating — рейтинг
@router.message(Command("rating"))
async def cmd_rating(message: types.Message):
    title = get_quest_title()
    participants = get_participants()
    sorted_teams = sorted(participants, key=lambda x: x[4], reverse=True)
    text = f"🏆 {title}\n\n"
    for i, p in enumerate(sorted_teams, start=1):
        text += f"{i}. {p[3]} — {p[4]}💎 (+{p[7]} за ⌛)\n"
    await message.answer(text)

# ✅ /help — список команд
@router.message(Command("help"))
async def cmd_help(message: types.Message):
    text = "📋 *Доступные команды:*\n\n"
    text += "👤 *Для игроков:*\n"
    text += "/start — Начать работу с ботом\n"
    text += "/register — Зарегистрировать команду\n"
    text += "/rating — Посмотреть рейтинг\n"
    text += "/help — Показать это сообщение\n\n"

    if message.from_user.id in ADMIN_IDS:
        text += "🛠 *Для администраторов:*\n"
        text += "/startgame — Запустить игру\n"
        text += "/stopgame — Остановить игру\n"
        text += "/resetgame — Сбросить игру\n"
        text += "/broadcast <текст> — Сделать рассылку\n"
        text += "/changeleader <old_id> <new_id> — Сменить лидера\n"
        text += "/removeadmin — Снять права админа\n"

    await message.answer(text, parse_mode="Markdown")

# ✅ Отправка вопроса
async def send_question(bot: Bot, user_id: int, question_num: int, status_text: str = "", state_update=True, disable_buttons=False):
    data = get_question_data(question_num)
    if not data:
        set_end_time(user_id)
        update_status(user_id, "finished")
        await bot.send_message(user_id, "✅ Квест завершён! Спасибо за участие.")
        return

    if state_update:
        set_start_time(user_id)

    state = get_state(user_id)
    text = format_question_message(question_num, data, status_text, state)

    kb = None
    if not disable_buttons:
        kb = question_keyboard(data["hints"], state["hints"])

    if state["message_id"]:
        await bot.edit_message_text(chat_id=user_id, message_id=state["message_id"], text=text, reply_markup=kb)
    else:
        msg = await bot.send_message(user_id, text, reply_markup=kb)
        set_message_id(user_id, msg.message_id)

# ✅ Форматирование текста вопроса
def format_question_message(q_num, data, status_text, state):
    text = f"❓ Вопрос №{q_num}\n"
    if status_text:
        text += status_text + "\n"
    text += f"{data['question']}\n\n"

    if state["attempts"]:
        text += "Вы попробовали:\n"
        for a in state["attempts"]:
            text += f"- {a}\n"

    if state["hints"]:
        text += "\n"
        for i in state["hints"]:
            text += f"💎 Подсказка {i}: {data['hints'][i-1][0]}\n"

    return text

# ✅ Обработка подсказки
@router.callback_query(F.data.startswith("hint_"))
async def use_hint(callback: types.CallbackQuery, bot: Bot):
    hint_idx = int(callback.data.split("_")[1])
    status = get_status(callback.from_user.id)
    q_data = get_question_data(int(status))
    price = q_data["hints"][hint_idx-1][1]

    update_score(callback.from_user.id, -price)
    add_hint(callback.from_user.id, hint_idx)
    await send_question(bot, callback.from_user.id, int(status), "💡 Вы взяли подсказку", state_update=False)
    await callback.answer()

# ✅ Обработка пропуска
@router.callback_query(F.data == "skip")
async def skip_question(callback: types.CallbackQuery, bot: Bot):
    status = get_status(callback.from_user.id)

    await send_question(bot, callback.from_user.id, int(status), "🎟️ Вопрос пропущен 🎟️", state_update=False, disable_buttons=True)

    update_score(callback.from_user.id, -SKIP_PENALTY)
    next_q = int(status) + 1
    init_player_state(callback.from_user.id)
    update_status(callback.from_user.id, next_q)

    await send_question(bot, callback.from_user.id, next_q, "")
    await callback.answer()
