import requests
import os
import time
from deep_translator import GoogleTranslator # වඩාත් දියුණු පරිවර්තකයක්

# --- CONFIGURATION ---
GNEWS_API_KEY = "86f195de5c480015cafdc7ea88a7fbbe"
CURRENTS_API_KEY = "jI57sNhl7dVvjajpjYBmgTQIM6MQzNgg-Zv12wPUXXPEFeng"
WHAPI_TOKEN = os.getenv('WHATSAPP_API_TOKEN')
CHANNEL_ID = os.getenv('WHATSAPP_CHANNEL')
DB_FILE = "sent_news.txt"

# AI Translator එක සෙට් කිරීම
translator = GoogleTranslator(source='en', target='si')

def get_sent_urls():
    if not os.path.exists(DB_FILE): return []
    with open(DB_FILE, "r") as f:
        return f.read().splitlines()

def save_sent_url(url):
    with open(DB_FILE, "a") as f:
        f.write(url + "\n")

def ai_translate(text):
    if not text: return ""
    try:
        # අකුරු 5000ක් දක්වා එකවර ඉතා නිවැරදිව පරිවර්තනය කරයි
        return translator.translate(text)
    except Exception as e:
        print(f"Translation Error: {e}")
        return text

def send_to_whatsapp(title, body, link, img):
    url = "https://gate.whapi.cloud/messages/image"
    # සාරාංශගත අන්තර්ගතය සහ Main Title එක පිරිසිදුව මෙතනින් සකස් වේ
    caption = (
        f"🔴 *{title}*\n\n"
        f"📝 *පුවත් සාරාංශය:*\n{body}\n\n"
        f"🔗 *සම්පූර්ණ විස්තරය කියවන්න:* {link}\n\n"
        f"📢 *BBC FLASH 24/7 Updates*"
    )
    payload = {"media": img, "to": CHANNEL_ID, "caption": caption}
    headers = {"authorization": f"Bearer {WHAPI_TOKEN}", "content-type": "application/json"}
    requests.post(url, json=payload, headers=headers)

# පුවත් එකතු කිරීම
all_news = []

# 1. GNews (ප්‍රධාන පුවත් 5ක්)
try:
    gn_url = f"https://gnews.io/api/v4/top-headlines?category=general&lang=en&apikey={GNEWS_API_KEY}&max=5"
    gn_data = requests.get(gn_url).json()
    for art in gn_data.get('articles', []):
        all_news.append({'title': art['title'], 'desc': art['description'], 'url': art['url'], 'img': art['image']})
except: pass

# 2. Currents API (තවත් පුවත් 5ක්)
try:
    cur_url = f"https://api.currentsapi.services/v1/latest-news?apiKey={CURRENTS_API_KEY}"
    cur_data = requests.get(cur_url).json()
    for art in cur_data.get('news', [])[:5]:
        all_news.append({'title': art['title'], 'desc': art['description'], 'url': art['url'], 'img': art['image']})
except: pass

sent_list = get_sent_urls()
count = 0

for news in all_news:
    if news['url'] not in sent_list and count < 10:
        # ඉතා නිවැරදි AI පරිවර්තනය
        s_title = ai_translate(news['title'])
        s_desc = ai_translate(news['desc'])
        
        # WhatsApp යැවීම
        send_to_whatsapp(s_title, s_desc, news['url'], news['img'])
        save_sent_url(news['url'])
        count += 1
        time.sleep(3) # බ්ලොක් නොවී සිටීමට තත්පර 3ක විරාමයක්

print(f"Uploaded {count} high-quality news updates.")

