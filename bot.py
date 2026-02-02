import requests
import os
from datetime import datetime, timedelta, timezone

# قراءة المتغيرات من GitHub Secrets
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
# التعامل مع TOPIC_ID بحذر لتجنب الأخطاء إذا كان فارغاً
try:
    TOPIC_ID = int(os.environ.get("TOPIC_ID", 0))
except ValueError:
    TOPIC_ID = None

EMULATORS = {
    "PCSX2": {"repo": "PCSX2/pcsx2", "platform": "PC / Steam Deck"},
    "RPCS3": {"repo": "RPCS3/rpcs3", "platform": "PC / Steam Deck"},
    "Dolphin": {"repo": "dolphin-emu/dolphin", "platform": "PC / Steam Deck"},
    "NetherSX2": {"repo": "Trixarian/NetherSX2-classic", "platform": "Android"}
}

def translate(text):
    # استخدام خدمة ترجمة مجانية (قد تكون غير مستقرة أحياناً)
    try:
        url = "https://libretranslate.de/translate"
        data = {"q": text, "source": "en", "target": "ar", "format": "text"}
        r = requests.post(url, data=data, timeout=5) # مهلة 5 ثواني
        if r.status_code == 200:
            return r.json().get("translatedText", text)
    except Exception as e:
        print(f"Translation failed: {e}")
    return text # إعادة النص الأصلي في حال فشل الترجمة

def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML", # لتنسيق الرسالة بشكل جميل
        "disable_web_page_preview": True
    }
    # إضافة Topic ID فقط إذا كان موجوداً
    if TOPIC_ID:
        payload["message_thread_id"] = TOPIC_ID
        
    try:
        r = requests.post(url, json=payload)
        print(f"Message sent: {r.status_code}")
    except Exception as e:
        print(f"Failed to send message: {e}")

def main():
    print("Starting check...")
    for name, data in EMULATORS.items():
        repo = data["repo"]
        api = f"https://api.github.com/repos/{repo}/releases/latest"
        
        try:
            r = requests.get(api)
            if r.status_code != 200:
                print(f"Error fetching {name}: {r.status_code}")
                continue

            release = r.json()
            
            # --- أهم تعديل: التحقق من التاريخ ---
            # GitHub يعطي الوقت بصيغة ISO 8601
            published_at_str = release.get('published_at')
            if not published_at_str: continue

            # تحويل النص إلى تاريخ ووقت
            published_at = datetime.fromisoformat(published_at_str.replace('Z', '+00:00'))
            
            # الوقت الحالي (UTC)
            now = datetime.now(timezone.utc)
            
            # حساب الفرق: هل نُشر التحديث خلال الـ 7 ساعات الماضية؟
            # (بما أن البوت يعمل كل 6 ساعات، نضع هامش ساعة إضافية)
            if (now - published_at) > timedelta(hours=7):
                print(f"Skipping {name}: Old update ({published_at})")
                continue
            # -------------------------------------

            body = release.get("body", "")
            # نأخذ أول 300 حرف فقط لتسريع الترجمة وتجنب الأخطاء
            short_body = body[:300] + "..." if len(body) > 300 else body
            translated = translate(short_body) if short_body else "تحديثات تقنية وتحسينات في الأداء."

            msg = f"""<b>🔔 تحديث جديد – {name}</b>

<b>🖥️ المنصة:</b> {data['platform']}
<b>📦 الإصدار:</b> {release.get('name')}

<b>⚙️ أبرز التغييرات:</b>
{translated}

<b>🔗 <a href="{release.get('html_url')}">رابط التحميل والمصدر</a></b>

📅 <i>{published_at_str[:10]}</i>
"""
            send_message(msg)

        except Exception as e:
            print(f"Error processing {name}: {e}")

# تصحيح الخطأ الإملائي هنا
if __name__ == "__main__":
    main()
