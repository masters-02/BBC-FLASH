import requests
import os
import time
import json

# --- API Keys ---
GNEWS_API_KEY = "86f195de5c480015cafdc7ea88a7fbbe"
CURRENTS_API_KEY = "jI57sNhl7dVvjajpjYBmgTQIM6MQzNgg-Zv12wPUXXPEFeng"
NEWS_API_KEY = "29c4923713d0493ab21959fca5d18184"
GEMINI_API_KEY = "AIzaSyD8nEhSKb1MzVuPSDK3dTV4qWsJP2merb4" 

WHAPI_TOKEN = os.getenv('WHATSAPP_API_TOKEN')
CHANNEL_ID = os.getenv('WHATSAPP_CHANNEL')
DB_FILE = "sent_news.txt"

def get_sent_urls():
    if not os.path.exists(DB_FILE): return []
    with open(DB_FILE, "r") as f:
        return f.read().splitlines()

def save_sent_url(url):
    with open(DB_FILE, "a") as f:
        f.write(url + "\n")

# Gemini කෙලින්ම API හරහා සම්බන්ධ කිරීම
def translate_and_expand(title, desc):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    # AI එකට දෙන දැඩි උපදෙස (Prompt)
    prompt = f"""ඔබ වෘත්තීය සිංහල පුවත්පත් කලාවේදියෙකි. පහතින් දී ඇත්තේ පුවතක මාතෘකාව සහ කෙටි සාරාංශයක් පමණි. ඔබගේ ලෝක දැනුම ද භාවිතා කර, මෙය සම්පූර්ණ, සවිස්තරාත්මක, දිගු පුවත් ලිපියක් ලෙස පිරිසිදු සිංහලෙන් ලියා දක්වන්න. 
අනිවාර්ය නීති:
1. කිසිදු ඉංග්‍රීසි වචනයක් භාවිතා නොකරන්න.
2. මාතෘකාව (Title) වෙනම ආකර්ෂණීයව දක්වන්න.
3. කරුණු ගොනුකර (Bullet points) පැහැදිලිව දක්වන්න.

English Title: {title}
English Short Description: {desc}"""

    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.4,
            "maxOutputTokens": 2048
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        result = response.json()
        
        # නිවැරදිව පිළිතුර ආවා නම් එය ලබා ගැනීම
        if "candidates" in result:
            return result["candidates"][0]["content"]["parts"][0]["text"].strip()
        else:
            print(f"Gemini API Error Details: {result}")
            return f"*{title}*\n\n{desc}" # Error එකක් ආවොත් පමණක් ඉංග්‍රීසි යවයි
    except Exception as e:
        print(f"Connection Error: {e}")
        return f"*{title}*\n\n{desc}"

def send_to_whatsapp(translated_text, link, img):
    url = "https://gate.whapi.cloud/messages/image"
    caption = f"📢 *ලෝක පුවත් සේවය*\n\n{translated_text}\n\n🔗 *මූලාශ්‍රය (Source):* {link}"
    
    payload = {
        "media": img, 
        "to": CHANNEL_ID,
        "caption": caption
    }
    headers = {"authorization": f"Bearer {WHAPI_TOKEN}", "content-type": "application/json"}
    response = requests.post(url, json=payload, headers=headers)
    print(f"WhatsApp Status: {response.status_code}")

# පුවත් මූලාශ්‍ර වලින් පුවත් ලබා ගැනීම
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
        img_url = art.get('urlToImage') or "https://upload.wikimedia.org/wikipedia/commons/6/62/BBC_News_2019.svg"
        all_news.append({'title': art.get('title'), 'desc': art.get('description'), 'url': art.get('url'), 'img': img_url})
except: pass

sent_list = get_sent_urls()
count = 0

for news in all_news:
    # පුවත් 11ක් පමණක් තෝරා ගැනීම
    if news['url'] not in sent_list and count < 11:
        print(f"Processing News {count+1}: {news['title']}")
        
        # සම්පූර්ණ දිගු සිංහල විස්තරය AI හරහා ලිවීම
        final_content = translate_and_expand(news['title'], news['desc'])
        
        # WhatsApp වෙත යැවීම
        send_to_whatsapp(final_content, news['url'], news['img'])
        save_sent_url(news['url'])
        
        count += 1
        time.sleep(10) # API Limit එකට අසුනොවීමට තත්පර 10ක් රැඳී සිටීම

print(f"Successfully uploaded {count} full news updates.")
