# notify.py
import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env (if present)
load_dotenv()

# Get Telegram credentials from environment variables
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def send_alert(message: str):
    """
    Send a Telegram message using the bot token and chat ID.

    Parameters:
        message (str): The alert message to send.
    """
    if not TOKEN or not CHAT_ID:
        print("⚠️ Telegram credentials not set. Skipping alert.")
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


# Example usage (for testing)
if __name__ == "__main__":
    send_alert("🚨 Test alert from Edge-AI IoT Anomaly Detection!")
