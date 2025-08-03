# keyboards.py
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton

def question_keyboard(hints, used_hints):
    kb = InlineKeyboardBuilder()
    # Первый ряд — подсказки
    for i, (_, price) in enumerate(hints, start=1):
        if i not in used_hints:
            kb.add(InlineKeyboardButton(text=f"HELP{i} -{price}💎", callback_data=f"hint_{i}"))
    kb.adjust(len(hints))  # Распределяем в ряд

    # Второй ряд — пропуск
    kb.row(InlineKeyboardButton(text="🎟️Пропустить (-3💎)", callback_data="skip"))

    return kb.as_markup()
