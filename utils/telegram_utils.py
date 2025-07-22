# utils/telegram_utils.py

import requests

# 🔧 Замените на свои данные
BOT_TOKEN = "ВАШ_ТОКЕН_БОТА"
CHAT_ID = "ВАШ_CHAT_ID"  # Можно узнать у @userinfobot

def send_telegram_message(message: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }
    try:
        response = requests.post(url, data=payload, timeout=5)
        if response.status_code != 200:
            print("[Telegram] Ошибка:", response.text)
    except Exception as e:  # noqa: F841
        print
