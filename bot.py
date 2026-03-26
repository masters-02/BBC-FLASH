        return f"*{title}*\n\n{desc}"
import requests
import os
import time
import google.generativeai as genai

# --- API Keys සහ Configurations ---
GNEWS_API_KEY = "86f195de5c480015cafdc7ea88a7fbbe"
CURRENTS_API_KEY = "jI57sNhl7dVvjajpjYBmgTQIM6MQzNgg-Zv12wPUXXPEFeng"
NEWS_API_KEY = "29c4923713d0493ab21959fca5d18184"
GEMINI_API_KEY = "AIzaSyD8nEhSKb1MzVuPSDK3dTV4qWsJP2merb4" # ඔබ ලබාදුන් Key එක

WHAPI_TOKEN = os.getenv('WHATSAPP_API_TOKEN')
CHANNEL_ID = os.getenv('WHATSAPP_CHANNEL')
DB_FILE = "sent_news.txt"

# --- ඔබ ලබාදුන් Gemini AI සැකසුම ---
genai.configure(api_key=GEMINI_API_KEY)

generation_config = {
  "temperature": 0.3, # නිරවද්‍යතාවය වැඩි කිරීමට අඩු අගයක්
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 2048,
}

model = genai.GenerativeModel(
  model_name="gemini-1.5-flash",
  generation_config=generation_config,
  system_instruction="ඔබ වෘත්තීය සිංහල පරිවර්තකයෙකි. ඕනෑම ඉංග්‍රීසි පුවතක් 100% පිරිසිදු, ව්‍යාකරණානුකූල හෙළ බසට පරිවර්තනය කරන්න. \n\nනීති:\n1. කිසිදු ඉංග්‍රීසි වචනයක් සිංහල අකුරින්වත් (උදා: 'බස්') භාවිතා නොකරන්න, ඒ වෙනුවට ගැළපෙන හෙළ වදන් (උදා: 'බස් රිය / පොදු ප්‍රවාහන රිය') භාවිතා කරන්න.\n2. උක්ත-ආඛ්‍යාත සම්බන්ධය (Subject-Verb Agreement) 100% නිවැරදි විය යුතුය.\n3. ප්‍රවෘත්ති ශීර්ෂය වඩාත් ආකර්ෂණීය සහ පැහැදිලි විය යුතුය.\n4. වාක්‍ය රටාව ස්වාභාවික සිංහල විය යුතුය (අප්‍රාණික පරිවර්තන එපා)."
)

def get_sent_urls():
    if not os.path.exists(DB_FILE): return []
    with open(DB_FILE, "r") as f:
        return f.read().splitlines()

def save_sent_url(url):
    with open(DB_FILE, "a") as f:
        f.write(url + "\n")

def translate_to_pure_sinhala(title, desc):
    try:
        # සම්පූර්ණ පුවතම සකස් කිරීමට දෙන උපදෙස
        prompt = f"පහත පුවතේ සම්පූර්ණ අන්තර්ගතය කියවා එය ආකර්ෂණීය මාතෘකාවක් සහ සවිස්තරාත්මක සාරාංශයක් සහිතව සිංහලට පරිවර්තනය කරන්න:\n\nTitle: {title}\nDescription: {desc}"
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"දෝෂයක් සිදු විය: {str(e)}")
        return f"*{title}*\n\n{desc}"

def send_to_whatsapp(translated_text, link, img):
    url = "https://gate.whapi.cloud/messages/image"
    caption = f"📢 *BBC FLASH*\n\n{translated_text}\n\n🔗 *සම්පූර්ණ පුවත කියවන්න:* {link}"
    
    payload = {
        "media": img, # නිවැරදි පින්තූරය මෙතැනින් යැවේ
        "to": CHANNEL_ID,
        "caption": caption
    }
    headers = {"authorization": f"Bearer {WHAPI_TOKEN}", "content-type": "application/json"}
    requests.post(url, json=payload, headers=headers)

# --- පුවත් මූලාශ්‍ර වලින් පුවත් ලබා ගැනීම ---
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
    # පුවත් 11ක් පමණක් තෝරා ගැනීම සහ Duplicate නැති බව තහවුරු කිරීම
    if news['url'] not in sent_list and count < 11:
        
        # 100% පිරිසිදු සිංහල පරිවර්තනය ලබා ගැනීම
        final_content = translate_to_pure_sinhala(news['title'], news['desc'])
        
        # පින්තූරය සමඟ WhatsApp වෙත යැවීම
        send_to_whatsapp(final_content, news['url'], news['img'])
        
        # යැවූ පුවත Database එකේ සේව් කිරීම
        save_sent_url(news['url'])
        
        count += 1
        print(f"Sent news {count}/11 successfully.")
        
        # Gemini API එකෙහි Rate Limits වලට හසු නොවීම සඳහා තත්පර 8ක විරාමයක්
        time.sleep(8)

print(f"Successfully uploaded {count} popular news updates.")
