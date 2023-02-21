import os
from dotenv import load_dotenv

load_dotenv()
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
GROUP_ID = int(os.getenv("GROUP_ID"))
CHAT_ID = int(os.getenv("CHAT_ID"))
BOT_NAME = os.getenv("BOT_NAME")
DB_CONFIG = os.getenv("DB_CONFIG")

temp_texts = {
    'WELCOMING': 'Привет!',
    'BYEBYING': 'Пока(',
    'KICK_TEXT': 'Кышь мышь',
    'STATUS1': 'Активчик',
    'STATUS2': 'Элита',
    'STATUS3': 'Тестер',
    'STATUS4': 'Команда',
    'STATUS5': 'Лидер',
    'PREDS': 5,
}

mailing = True
