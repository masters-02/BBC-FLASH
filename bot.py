import requests
import os
import time
import google.generativeai as genai

# --- CONFIGURATION ---
GNEWS_API_KEY = "86f195de5c480015cafdc7ea88a7fbbe"
CURRENTS_API_KEY = "jI57sNhl7dVvjajpjYBmgTQIM6MQzNgg-Zv12wPUXXPEFeng"
NEWS_API_KEY = "29c4923713d0493ab21959fca5d18184"
GEMINI_API_KEY = "AIzaSyD8nEhSKb1MzVuPSDK3dTV4qWsJP2merb4"
WHAPI_TOKEN = os.getenv('WHATSAPP_API_TOKEN')
CHANNEL_ID = os.getenv('WHATSAPP_CHANNEL')
DB_FILE = "sent_news.txt"

# Gemini AI Setup
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction="ඔබ වෘත්තීය සිංහල පුවත්පත් කලාවේදියෙකි. ඉංග්‍රීසි පුවතක් කියවා එහි සම්පූර්ණ අන්තර්ගතය 100% පිරිසිදු හෙළ බසට හරවන්න. ප්‍රධාන මාතෘකාව (Title) කැපී පෙනෙන ලෙසත්, අන්තර්ගතය වැදගත් කරුණු සහිතව සාරාංශගත කර (Summary with bullet points) ඉදිරිපත් කරන්න. කිසිදු ඉංග්‍රීසි වචනයක් භාවිතා නොකරන්න."
)

def get_sent_urls():
    if not os.path.exists(DB_FILE): return []
    with open(DB_FILE, "r") as f:
        return f.read().splitlines()

def save_sent_url(url):
    with open(DB_FILE, "a") as f:
        f.write(url + "\n")

def gemini_translate(title, desc):
    try:
        prompt = f"කරුණාකර මෙම පුවත ආකර්ෂණීය මාතෘකාවක් සහ වැදගත් කරුණු සහිත සම්පූර්ණ විස්තරයක් ලෙස සිංහලට පරිවර්තනය කරන්න:\nTitle: {title}\nDescription: {desc}"
        response = model.generate_content(prompt)
        return response.text
    except:
        return f"*{title}*\n\n{desc}"

def send_to_whatsapp(content, link, img):
    url = "https://gate.whapi.cloud/messages/image"
    caption = f"📢 *ලෝක පුවත් සේවය*\n\n{content}\n\n🔗 *සම්පූර්ණ පුවත කියවන්න:* {link}"
    payload = {"media": img, "to": CHANNEL_ID, "caption": caption}
    headers = {"authorization": f"Bearer {WHAPI_TOKEN}", "content-type": "application/json"}
    requests.post(url, json=payload, headers=headers)

# පුවත් මූලාශ්‍ර එකතු කිරීම
all_news = []

# 1. GNews
try:
    gn = requests.get(f"https://gnews.io/api/v4/top-headlines?category=general&lang=en&apikey={GNEWS_API_KEY}&max=10").json()
    for art in gn.get('articles', []):
        all_news.append({'title': art['title'], 'desc': art['description'], 'url': art['url'], 'img': art['image']})
except: pass

# 2. Currents
try:
    cur = requests.get(f"https://api.currentsapi.services/v1/latest-news?apiKey={CURRENTS_API_KEY}").json()
    for art in cur.get('news', []):
        all_news.append({'title': art['title'], 'desc': art['description'], 'url': art['url'], 'img': art['image']})
except: pass

# 3. NewsAPI
try:
    napi = requests.get(f"https://newsapi.org/v2/top-headlines?sources=bbc-news&apiKey={NEWS_API_KEY}").json()
    for art in napi.get('articles', []):
        all_news.append({'title': art.get('title'), 'desc': art.get('description'), 'url': art.get('url'), 'img': art.get('urlToImage')})
except: pass

sent_list = get_sent_urls()
count = 0

for news in all_news:
    if news['url'] not in sent_list and count < 11:
        # Gemini AI මගින් සම්පූර්ණ විස්තරය සකස් කිරීම
        final_content = gemini_translate(news['title'], news['desc'])
        
        # WhatsApp වෙත යැවීම
        send_to_whatsapp(final_content, news['url'], news['img'])
        save_sent_url(news['url'])
        
        count += 1
        time.sleep(10) # Gemini limit එකට හසුවීම වැළැක්වීමට තත්පර 10ක විරාමයක්

print(f"Successfully uploaded {count} popular news updates.")
