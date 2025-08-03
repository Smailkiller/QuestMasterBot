# config.py
import os
import asyncio

# 🔑 Токен Telegram бота
TOKEN = "ВАШ ТОКЕН"

# 📂 Пути
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MEDIA_DIR = os.path.join(BASE_DIR, "media")
EXCEL_FILE = os.path.join(MEDIA_DIR, "QustData.xlsx")

# 🎮 Начальные параметры
START_SCORE = 10
SKIP_PENALTY = 3

# 🛡 Администраторы
ADMIN_IDS = set()
ADMIN_PASSWORD = "MySecret123"

# 🔒 Блокировка для Excel
excel_lock = asyncio.Lock()

# 💎 Бонусы за скорость (топ-3)
SPEED_BONUSES = [3, 2, 1]
