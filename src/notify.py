import os
import requests

# Read secrets from environment variables
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def send_alert(message: str):
    if not TOKEN or not CHAT_ID:
        print("Telegram credentials not set. Skipping alert.")
        return

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }

    try:
        response = requests.post(url, data=payload, timeout=5)
        print("Telegram response:", response.text)
    except Exception as e:
        print("Error sending Telegram alert:", e)
