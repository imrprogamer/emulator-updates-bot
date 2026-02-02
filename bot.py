import requests
import os
from datetime import datetime

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
TOPIC_ID = int(os.environ["TOPIC_ID"])

EMULATORS = {
    "PCSX2": {
        "repo": "PCSX2/pcsx2",
        "platform": "PC / Steam Deck"
    },
    "RPCS3": {
        "repo": "RPCS3/rpcs3",
        "platform": "PC / Steam Deck"
    },
    "Dolphin": {
        "repo": "dolphin-emu/dolphin",
        "platform": "PC / Steam Deck"
    },
    "NetherSX2": {
        "repo": "Trixarian/NetherSX2-classic",
        "platform": "Android"
    }
}

def translate(text):
    url = "https://libretranslate.de/translate"
    data = {
        "q": text,
        "source": "en",
        "target": "ar",
        "format": "text"
    }
    r = requests.post(url, data=data, timeout=30)
    return r.json().get("translatedText", "")

def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "message_thread_id": TOPIC_ID,
        "text": text
    }
    requests.post(url, json=payload)

def main():
    for name, data in EMULATORS.items():
        repo = data["repo"]
        api = f"https://api.github.com/repos/{repo}/releases/latest"
        r = requests.get(api)
        if r.status_code != 200:
            continue

        release = r.json()
        body = release.get("body", "")
        translated = translate(body) if body else "لا توجد تفاصيل."

        msg = f"""🔔 تحديث جديد – {name} Emulator

🖥️ المنصة:
{data['platform']}

📦 الإصدار:
{release.get('name')}

⚙️ أبرز التغييرات:
{translated}

🔗 المصدر:
{release.get('html_url')}

📅 التاريخ:
{release.get('published_at')[:10]}
"""
        send_message(msg)

if name == "main":
    main()
