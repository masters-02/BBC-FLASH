import feedparser
import requests
import os
from googletrans import Translator

# Config
RSS_FEED_URL = "http://feeds.bbci.co.uk/news/world/rss.xml"
WHAPI_TOKEN = os.getenv('WHATSAPP_API_TOKEN')
CHANNEL_ID = os.getenv('WHATSAPP_CHANNEL')

translator = Translator()

def send_status_msg(text):
    url = "https://gate.whapi.cloud/messages/text"
    payload = {
        "to": CHANNEL_ID,
        "body": text
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {WHAPI_TOKEN}"
    }
    requests.post(url, json=payload, headers=headers)

def send_whatsapp_media(title_si, summary_si, link, image_url):
    url = "https://gate.whapi.cloud/messages/image"
    caption = f"🔴 *BBC Flash NEWS*\n\n📌 *{title_si}*\n\n📝 {summary_si}\n\n🔗 වැඩිදුර විස්තර: {link}"
    
    payload = {
        "media": image_url,
        "to": CHANNEL_ID,
        "caption": caption
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {WHAPI_TOKEN}"
    }
    requests.post(url, json=payload, headers=headers)

# 1. වැඩේ පටන් ගන්න කොටම Status Message එකක් යවනවා
send_status_msg("🔄 *News Update Soon...*")

# 2. පුවත් කියවීම
feed = feedparser.parse(RSS_FEED_URL)

if feed.entries:
    item = feed.entries[0]
    title_en = item.title
    summary_en = item.description
    link = item.link
    
    image_url = ""
    if 'media_thumbnail' in item:
        image_url = item.media_thumbnail[0]['url']
    else:
        image_url = "https://upload.wikimedia.org/wikipedia/commons/6/62/BBC_News_2019.svg"

    try:
        title_si = translator.translate(title_en, dest='si').text
        summary_si = translator.translate(summary_en, dest='si').text
        
        # 3. පුවත යැවීම
        send_whatsapp_media(title_si, summary_si, link, image_url)
        print("Success!")
    except Exception as e:
        print(f"Error: {e}")

