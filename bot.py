import requests
import os
from googletrans import Translator

# --- CONFIGURATION ---
NEWS_API_KEY = "29c4923713d0493ab21959fca5d18184" # ඔබ ලබා දුන් API Key එක
WHAPI_TOKEN = os.getenv('WHATSAPP_API_TOKEN')
CHANNEL_ID = os.getenv('WHATSAPP_CHANNEL')

translator = Translator()

def send_status_msg(text):
    url = "https://gate.whapi.cloud/messages/text"
    payload = {"to": CHANNEL_ID, "body": text}
    headers = {"authorization": f"Bearer {WHAPI_TOKEN}", "content-type": "application/json"}
    requests.post(url, json=payload, headers=headers)

def send_whatsapp_media(title_si, summary_si, link, image_url):
    url = "https://gate.whapi.cloud/messages/image"
    caption = f"🔴 *BBC Flash NEWS*\n\n📌 *{title_si}*\n\n📝 {summary_si}\n\n🔗 වැඩිදුර විස්තර: {link}"
    payload = {"media": image_url, "to": CHANNEL_ID, "caption": caption}
    headers = {"authorization": f"Bearer {WHAPI_TOKEN}", "content-type": "application/json"}
    response = requests.post(url, json=payload, headers=headers)
    print(f"WhatsApp Response: {response.status_code} - {response.text}")

# 1. ආරම්භක පණිවිඩය
send_status_msg("🔄 *News Update Soon...*")

# 2. NewsAPI හරහා අලුත්ම පුවත් ලබා ගැනීම
# bbc-news මූලාශ්‍රයෙන් අලුත්ම පුවත් ගෙන්වා ගැනීම
news_url = f"https://newsapi.org/v2/top-headlines?sources=bbc-news&apiKey={NEWS_API_KEY}"
response = requests.get(news_url)
data = response.json()

if data.get("status") == "ok" and data.get("articles"):
    # පළමු පුවත තෝරා ගැනීම
    article = data["articles"][0]
    title_en = article.get("title")
    summary_en = article.get("description")
    link = article.get("url")
    image_url = article.get("urlToImage")

    if not image_url:
        image_url = "https://upload.wikimedia.org/wikipedia/commons/6/62/BBC_News_2019.svg"

    try:
        # 3. සිංහලට පරිවර්තනය (AI Translation)
        title_si = translator.translate(title_en, src='en', dest='si').text
        summary_si = translator.translate(summary_en, src='en', dest='si').text
        
        # 4. WhatsApp වෙත යැවීම
        send_whatsapp_media(title_si, summary_si, link, image_url)
        print("Success: News sent successfully!")
        
    except Exception as e:
        print(f"Translation Error: {e}")
else:
    print(f"Error fetching news: {data.get('message')}")
